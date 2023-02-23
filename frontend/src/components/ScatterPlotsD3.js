import React, {useState, useEffect, useRef} from 'react';
import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js';
import * as d3 from 'd3';
import * as constants from "../modules/Constants.js";
import PCA from '../modules/PCA.js';



function valToShape(vals,size,arcType='T'){
    //set arctype to "T" if you want curves
    var arcLength = 2*Math.PI/vals.length;
    let string = 'M 0,'+ (-size)+ ' '
    var makeline = (i,angle) => {
        let v0 = vals[i];
        let v1 = vals[i%vals.length];
        let [x0,y0] = Utils.radToCartesian(angle);
        let [x1,y1] = Utils.radToCartesian(angle+arcLength);
        let newString = " L" + v0*size*x0 + ',' + v0*size*y0
        // + ' ' + arcType + ' ' + v0*size*x0 + ',' + v0*size*y0 
        // + ' ' + v1*size*x1 + ',' + v1*size*y1;
         + ' L' + v1*size*x1 + ',' + v1*size*y1;
        return  newString;
    }
    let currAngle = -Math.PI/2;
    vals = vals.map(d=>d);
    vals.push(vals[0]);
    for(let i in vals){
        string = string + makeline(i,currAngle);
        currAngle += arcLength;
    }
    return  string; //+ circlePath(size);
}



function notAllZero(array){
    if(array === undefined){
        return false
    }
    for(let value of array){
        //the big value is because I have a bug in the preprocessing and it means it is also missing
        if(value > 1 & value < 10000000){
            return true
        }
    }
    return false
}


export default function ScatterPlotD3(props){

    const d3Container = useRef(null);
    const [svg, height, width, tTip] = useSVGCanvas(d3Container);
    const [brushedPatient,setBrushedPatient] = useState(4663235737);
    const [getTransform,setGetTransform] = useState(null);
    const radius = 10;
    const padding = 40;
    const plotType = 'pca';

    const skipRois = [];

    function plotPCA(data){
        svg.selectAll().remove();
        console.log('pca',data)
        const rowOrder = data.rowOrder;
        const colOrder = data.colOrder;
        var plot_rois = [];
        for(let r of constants.ORGAN_PLOT_ORDER){
            if(colOrder.indexOf(r) > -1 & skipRois.indexOf(r) < 0){
                plot_rois.push(r);
            }
        }
        console.log('plot',plot_rois,constants.ORGAN_PLOT_ORDER)
        const plotColOrder = colOrder.map(roi => plot_rois.indexOf(roi)).filter(d => d > -1);
        const pids = Object.keys(data.distances);
        const gtvPos = rowOrder.indexOf('gtv');
        const gtvnPos = rowOrder.indexOf('gtvn');

        const fix = a => {
            a = a.slice(0,colOrder.length);
            a = a.map( d => d >= 10000000? 0:d)
            // return a
            return plotColOrder.map( i => a[i]) //only use plot_rois instead of all of them
        }
        //the last bit is because one of the entries has too many points. will fix later
        //if they're uneven the pca doesn't work
        let gtvPoints = pids.map( a => fix(data.distances[a][gtvPos]));
        let gtvnPoints = pids.map( a => fix(data.distances[a][gtvnPos]));

        const mergedPoints = gtvPoints.concat(gtvnPoints).filter(notAllZero);
        const distMin = d3.min(mergedPoints.map(a => Math.min(...a)));
        const distMax = d3.max(mergedPoints.map(a => Math.max(...a)));
        const pScale = d3.scalePow(2)
            .domain([distMax,2,0])
            .range([0.01,.6,1]);

        var pcaFit = PCA.getEigenVectors(mergedPoints);
        var gtvProjection = Utils.ApplyPca2D(gtvPoints,pcaFit);
        var gtvnProjection = Utils.ApplyPca2D(gtvnPoints,pcaFit);
        
        var allPoints = [];
        var links = [];
        
        

        function toProximity(distance){
            return distance === 0? 0: pScale(Math.max(0,distance));
        }

        for(let i in pids){
            let pid = pids[i];
            let gtvn = gtvnProjection[i];
            let gtv = gtvProjection[i];
            let link = {'patient':pid}
            if(notAllZero(gtvPoints[i])){
                let prox = gtvPoints[i].map(toProximity)
                let gtvPoint = {
                    'patient': pid, 
                    'x': gtv[0].valueOf(), 'y': gtv[1].valueOf(), 
                    'baseX': gtv[0].valueOf(), 'baseY': gtv[1].valueOf(), 
                    'type': 'gtv',
                    'id': pid+'gtv',
                    'original': prox,
                    'maxProximity': Math.max(...prox),
                }
                allPoints.push(gtvPoint);
                link.source = gtvPoint.id
            }
            if(notAllZero(gtvnPoints[i])){
                let prox= gtvnPoints[i].map(toProximity)
                let gtvnPoint = {
                    'patient': pid, 
                    'x': gtvn[0].valueOf(), 'y': gtvn[1].valueOf(), 
                    'baseX': gtvn[0].valueOf(), 'baseY': gtvn[1].valueOf(), 
                    'type': 'gtvn',
                    'id': pid+'gtvn',
                    'original': prox,
                    'maxProximity': Math.max(...prox),
                }
                allPoints.push(gtvnPoint);
                link.target = gtvnPoint.id;
            }
            if(link.source !== undefined & link.target !== undefined){
                links.push(link);
            }
        }


        const xScale = d3.scaleLinear()
            .domain(d3.extent(allPoints, d => d.baseX))
            .range([padding,width-padding]);

        const yScale = d3.scaleLinear()
            .domain(d3.extent(allPoints, d => d.baseY))
            .range([height-padding,padding]);

        for(let item of allPoints){
            item.x = xScale(item.baseX);
            item.y = yScale(item.baseY);
        }

        const proximityScale = d => d;
        const boundX = x => Math.min(Math.max(padding,x),width-padding);
        const boundY = y => Math.min(Math.max(y,padding),height-padding);
        const getX = d => boundX(d.x);
        const getY = d => boundY(d.y);

        const transform = d => 'translate(' + getX(d) + ',' + getY(d) + ')';
        const getColor = d => {
            if(props.parameters.patientIDs.indexOf(parseInt(d.patient)) > -1){
                return d.type === 'gtv'? 'red': 'orange';
            }
            return 'grey';
        }
        const getOpacity = d => d.type === 'gtv'? 1:.8;
        const getRadius = d => radius;//d.type === 'gtv'? 10:6;

        const getPath = d => {
            return valToShape(d.original.map(proximityScale),getRadius(d));
        }
        svg.selectAll('path').filter('.link').remove();
        let connections = svg.selectAll('path').filter('.link')
            .data(links).enter()
            .append('path').attr('class','.link')
            .attr('opacity', .3)
            .attr('fill','')
            .attr('fill-opacity',0)
            .attr('stroke', 'black')
            .attr('stroke-width', .8);

        var forceLink = d3.forceLink()
            .id(d=>d.id)
            .strength(0)
            .links(links);

        const linkFunc = d3.line();
        const linkArc = d => linkFunc([[getX(d.source),getY(d.source)],[getX(d.target),getY(d.target)]]);

        const className = 'gtvPoints';
        svg.selectAll('.'+className).remove();
        let svgPoints = svg.selectAll('path').filter('.'+className)
            .data(allPoints).enter()
            .append('path').attr('class',className)
            .attr('d',getPath)
            .attr('transform',transform)
            .attr('fill',getColor)
            .attr('stroke','black')
            .attr('stroke-width',1)
            .attr('fill-opacity',.95)
            .attr('stroke-opacity',1)
            .on('dblclick',function(e,d){
                if(props.parameters.patientIDs.indexOf(parseInt(d.patient)) > -1){
                    let newList = [parseInt(d.patient)];
                    props.setSelectedCloudIds(newList)
                }
            })
            .on('mouseover',function(e,d){
                let string =d.patient + '-' + d.type + '</br>';
                for(let i in d.original){
                    string += colOrder[i] + ': ' + d.original[i].toFixed(3) + '</br>'; 
                }
                tTip.html(string);
                setBrushedPatient(d.patient);
            }).on('mousemove', function(e){
                Utils.moveTTipEvent(tTip,e);
            }).on('mouseout', function(e){
                Utils.hideTTip(tTip);
                setBrushedPatient(null);
            });

        const tick = ()=>{
            connections.attr('d',linkArc);
            svgPoints.attr('transform',transform)
        }

        var simulation = d3.forceSimulation(allPoints)
            // .alphaMin(.001)
            .force('collide',d3.forceCollide().radius(d=>d.maxProximity*getRadius(d)).strength(.1))
            .force("center", d3.forceCenter().x(width/2).y(height/2).strength(.1))
            .force('link',forceLink)
            .on('tick',tick);

    }

    function plotRadVis(data){
        console.log('radvis',data);
        // svg.selectAll().remove();
        // console.log('pca',data)
        // const rowOrder = data.rowOrder;
        // const colOrder = data.colOrder;
        // var plotColOrder = colOrder.map(roi => plot_rois.indexOf(roi)).filter(d => d > -1);
        // const pids = Object.keys(data.distances);
        // const gtvPos = rowOrder.indexOf('gtv');
        // const gtvnPos = rowOrder.indexOf('gtvn');

        // const fix = a => {
        //     a = a.slice(0,colOrder.length);
        //     a = a.map( d => d >= 10000000? 0:d)
        //     // return a
        //     return plotColOrder.map( i => a[i]) //only use plot_rois instead of all of them
        // }
        // //the last bit is because one of the entries has too many points. will fix later
        // //if they're uneven the pca doesn't work
        // let gtvPoints = pids.map( a => fix(data.distances[a][gtvPos]));
        // let gtvnPoints = pids.map( a => fix(data.distances[a][gtvnPos]));

        // const mergedPoints = gtvPoints.concat(gtvnPoints).filter(notAllZero);
        // const distMin = d3.min(mergedPoints.map(a => Math.min(...a)));
        // const distMax = d3.max(mergedPoints.map(a => Math.max(...a)));
        // const pScale = d3.scalePow(2)
        //     .domain([distMax,2,0])
        //     .range([0.01,.6,1]);


        // const arcLength = 2*Math.PI/colOrder.length;
        // const radialLength = Math.min((width/2)-padding, (height/2)-padding);
        // var forcePositions = [];
        // var currPos = -Math.PI/2;
        // for(let roi of colOrder){
        //     let arcOffset = Utils.radToCartesian(currPos,radialLength);
        //     let x = arcOffset[0] + width/2;
        //     let y = arcOffset[1] + height/2;
        //     let entry = {
        //         'x': x,
        //         'y': y,
        //         'roi': roi,
        //         'id': roi+'strength',
        //     }
        //     forcePositions.push(entry);
        //     currPos += arcLength;
        // }

        // function makeForceLinks(p){
        //     let strengths = p.proximities;
        //     let theseLinks = []
        //     for(let i in strengths){
        //         let forceItem = forcePositions[i];
        //         let power = strengths[i];
        //         if(power > 0.0001){
        //             let link = {
        //                 'source': forceItem.id,
        //                 'target': p.id,
        //                 'patient': p.patient,
        //                 'roi': forceItem.roi,
        //                 'strength': power,
        //             }
        //             theseLinks.push(link);
        //         }
        //     }
        //     return theseLinks
        // }


        // var allPoints = [];
        // var links = [];
        // var radLinks = [];
        // function toProximity(distance){
        //     return distance === 0? 0: pScale(Math.max(0,distance));
        // }

        // for(let i in pids){
        //     let pid = pids[i];
        //     let gtvn = gtvnPoints[i];
        //     let gtv = gtvPoints[i];
        //     let link = {'patient':pid}
        //     if(notAllZero(gtv)){
        //         let prox = gtv.map(toProximity)
        //         let gtvPoint = {
        //             'patient': pid, 
        //             'x': width/2, 'y': height/2,  
        //             'type': 'gtv',
        //             'id': pid+'gtv',
        //             'proximities': prox,
        //             'maxProximity': Math.max(...prox),
        //         }
        //         allPoints.push(gtvPoint);
        //         link.source = gtvPoint.id;
        //         radLinks.push(...makeForceLinks(gtvPoint));
        //     }
        //     if(notAllZero(gtvn)){
        //         let prox= gtvn.map(toProximity)
        //         let gtvnPoint = {
        //             'patient': pid, 
        //             'x': width/2, 'y': height/2,  
        //             'type': 'gtvn',
        //             'id': pid+'gtvn',
        //             'proximities': prox,
        //             'maxProximity': Math.max(...prox),
        //         }
        //         allPoints.push(gtvnPoint);
        //         link.target = gtvnPoint.id;
        //         radLinks.push(...makeForceLinks(gtvnPoint));
        //     }
        //     if(link.source !== undefined & link.target !== undefined){
        //         links.push(link);
        //     }
        // }

        // console.log('links',radLinks);


        // const proximityScale = d => d;
        // const boundX = x => Math.min(Math.max(padding,x),width-padding);
        // const boundY = y => Math.min(Math.max(y,padding),height-padding);
        // const getX = d => boundX(d.x);
        // const getY = d => boundY(d.y);

        // const transform = d => 'translate(' + getX(d) + ',' + getY(d) + ')';
        // const getColor = d => {
        //     if(props.parameters.patientIDs.indexOf(parseInt(d.patient)) > -1){
        //         return d.type === 'gtv'? 'red': 'orange';
        //     }
        //     return 'grey';
        // }
        // const getOpacity = d => d.type === 'gtv'? 1:.8;
        // const getRadius = d => radius;//d.type === 'gtv'? 10:6;

        // const getPath = d => {
        //     return valToShape(d.proximities.map(proximityScale),getRadius(d));
        // }

        // svg.selectAll('path').filter('.link').remove();
        // let connections = svg.selectAll('path').filter('.link')
        //     .data(links).enter()
        //     .append('path').attr('class','.link')
        //     .attr('opacity', .3)
        //     .attr('fill','')
        //     .attr('fill-opacity',0)
        //     .attr('stroke', 'black')
        //     .attr('stroke-width', .8);

        // var forceLink = d3.forceLink()
        //     .id(d=>d.id)
        //     .strength(0)
        //     .links(links);

        // var radVisForce = d3.forceLink()
        //     .id(d=>d.id)
        //     .strength(d=>d.power)
        //     .links(radLinks);

        // const linkFunc = d3.line();
        // const linkArc = d => linkFunc([[getX(d.source),getY(d.source)],[getX(d.target),getY(d.target)]]);

        // const className = 'gtvPoints';
        // svg.selectAll('.'+className).remove();
        // let svgPoints = svg.selectAll('path').filter('.'+className)
        //     .data(allPoints).enter()
        //     .append('path').attr('class',className)
        //     .attr('d',getPath)
        //     .attr('transform',transform)
        //     .attr('fill',getColor)
        //     .attr('stroke','black')
        //     .attr('stroke-width',1)
        //     .attr('fill-opacity',.95)
        //     .attr('stroke-opacity',1)
        //     .on('dblclick',function(e,d){
        //         if(props.parameters.patientIDs.indexOf(parseInt(d.patient)) > -1){
        //             let newList = [parseInt(d.patient)];
        //             props.setSelectedCloudIds(newList)
        //         }
        //     })
        //     .on('mouseover',function(e,d){
        //         let string =d.patient + '-' + d.type + '</br>';
        //         for(let i in d.original){
        //             string += colOrder[i] + ': ' + d.original[i].toFixed(3) + '</br>'; 
        //         }
        //         tTip.html(string);
        //         setBrushedPatient(d.patient);
        //     }).on('mousemove', function(e){
        //         Utils.moveTTipEvent(tTip,e);
        //     }).on('mouseout', function(e){
        //         Utils.hideTTip(tTip);
        //         setBrushedPatient(null);
        //     });

        // const tick = ()=>{
        //     connections.attr('d',linkArc);
        //     svgPoints.attr('transform',transform)
        // }

        // console.log('fp',forcePositions)
        // // let i = 0;
        // // let entry = forcePositions[i];
        // var simulation = d3.forceSimulation(allPoints.concat(forcePositions))
        //     .force('collide',d3.forceCollide().radius(d=>d.maxProximity*getRadius(d)).strength(.01))
        //     .force("center", d3.forceCenter().x(width/2).y(height/2).strength(.1))
        //     .force('link',forceLink)
        //     .force('radVis',radVisForce)
        //     .on('tick',tick)
        //     .stop();
        // // for(const i in forcePositions){
        // //     let entry = forcePositions[i];
        // //     simulation
        // //         .force(entry.roi + 'x',d3.forceX(entry.x).strength(d=>{
        // //             console.log('in d',d.proximities[i])
        // //             return d.proximities[i]
        // //         }))
        // //         .force(entry.roi + 'y',d3.forceY(entry.y))
        // // }
        // simulation.restart();


        
    }

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(props.distanceData)){
            if(plotType === 'radial'){ plotRadVis(props.distanceData); }
            else if(plotType == 'pca'){ plotPCA(props.distanceData); }
            else{
                console.log('bad scatterplot argument, using pca',plotType);
                plotPCA(props.distanceData);
            }
        }
    },[height,width,props.distanceData]);


    useEffect(()=>{
        if(svg === undefined){ return; }
        const isActive = d => d.patient === brushedPatient;
        if(brushedPatient === null){
            svg.selectAll('path')
                .style('opacity','');
        }
        else{
            svg.selectAll('path')
                .style('opacity',d=>isActive(d)? 1:.5);

            // if(getTransform !== null){
            //     console.log(getTransform)
            //     svg.selectAll('.gtvPoints')
            //         .attr('transform', d => isActive(d)? 'scale(3)' + getTransform(d): getTransform(d));
            // }
        }
    },[svg,brushedPatient])

    return (
        <div
            className={"d3-component"}
            style={{'height':'95%','width':'95%'}}
            ref={d3Container}
        ></div>
    );
}