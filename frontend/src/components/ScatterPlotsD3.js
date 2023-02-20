import React, {useState, useEffect, useRef} from 'react';
import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js';
import * as d3 from 'd3';
import PCA from '../modules/PCA.js'

function ApplyPca2D(array,eigenVectors){
    let result = PCA.computeAdjustedData(array,eigenVectors[0],eigenVectors[1]);
    //resut is 2xN -> transpose so its Nx2
    return PCA.transpose(result.formattedAdjustedData);
}


function Pca2D(array){
  //helper function to do pca for proejction on an array of arrays shape NxD -> Nx2
  let eVectors = PCA.getEigenVectors(array);
  return ApplyPca2D(array,eVectors);
}

function radToCartesian(angle,scale=1){
    angle = angle
    let x = Math.cos(angle)*scale;
    let y = Math.sin(angle)*scale;
    return [x,y];
}

function circlePath(r){
    let path = 'm 0,0 '
        + 'M ' + (-r) + ', 0 '
        + 'a ' + r + ',' + r + ' 0 1,0 ' + (2*r) + ',0 '
        + 'a ' + r + ',' + r + ' 0 1,0 ' + (-2*r) + ',0z';
    return path;
}

// function valToShape(vals,size){
//     let string = circlePath(size) + ' M 0,0 ';
//     var arcLength = 2*Math.PI/vals.length;
//     var makeline = (value,angle) => {
//         let [x,y] = radToCartesian(angle);
//         let newString = " L" + value*size*x + ',' + value*size*y + ' 0,0';
//         return  newString;
//     }
//     let currAngle = -Math.PI/2;
//     for(let v of vals){
//         string = string + makeline(v,currAngle);
//         currAngle += arcLength;
//     }
//     return string;
// }

function valToShape(vals,size){
    // let string = circlePath(size) + ' M 0,0 ';
    let string = 'M 0,0 '
    var arcLength = 2*Math.PI/vals.length;
    var makeline = (i,angle) => {
        let v0 = vals[i];
        let v1 = vals[i%vals.length];
        let [x0,y0] = radToCartesian(angle);
        let [x1,y1] = radToCartesian(angle+arcLength);
        let newString = " L" + v0*size*x0 + ',' + v0*size*y0
        + ' T ' + v0*size*x0 + ',' + v0*size*y0 + ' ' + v1*size*x1 + ',' + v1*size*y1;
         // + ' L' + v1*size*x1 + ',' + v1*size*y1;
        return  newString;
    }
    let currAngle = -Math.PI/2;
    for(let i in vals){
        string = string + makeline(i,currAngle);
        currAngle += arcLength;
    }
    return string + 'z ';//+ circlePath(size);
}

function toProximity(distance){
    return distance === 0? 0: 1/(1+distance);
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
    const radius = 10;
    const padding = 40;
    const plotType = 'pca';

    const plot_rois = ['tongue','ipc','spc','mpc',
    'hard_palate','soft_palate','esophagus','brainstem',
    'sternocleidomastoid_l','sternocleidomastoid_r']


    function plotPCA(data){
        svg.selectAll().remove();
        // console.log('pca',data)
        const rowOrder = data.rowOrder;
        const colOrder = data.colOrder;
        const plotColOrder = colOrder.map(roi => plot_rois.indexOf(roi)).filter(d => d > -1);
        // console.log('plot col',plotColOrder)
        const pids = Object.keys(data.distances);
        const gtvPos = rowOrder.indexOf('gtv');
        const gtvnPos = rowOrder.indexOf('gtvn');

        const fix = a => {
            a = a.map( d => d >= 10000000? 0:d)
            return a
            // return plotColOrder.map( i => a[i]) //only use plot_rois instead of all of them
        }
        let gtvPoints = pids.map( a => fix(data.distances[a][gtvPos]));
        let gtvnPoints = pids.map( a => fix(data.distances[a][gtvnPos]));

        // console.log('pre',gtvPoints,gtvnPoints,gtvPos,gtvnPos);
        // gtvPoints = gtvPoints.filter(notAllZero);
        // gtvnPoints = gtvnPoints.filter(notAllZero);
        var pcaFit = PCA.getEigenVectors(gtvPoints.concat(gtvnPoints).filter(notAllZero));
        var gtvProjection = ApplyPca2D(gtvPoints,pcaFit);
        var gtvnProjection = ApplyPca2D(gtvnPoints,pcaFit);
        
        var allPoints = [];
        var links = [];
        
        for(let i in pids){
            let pid = pids[i];
            let gtvn = gtvnProjection[i];
            let gtv = gtvProjection[i];
            let link = {'patient':pid}
            if(notAllZero(gtvPoints[i])){
                let gtvPoint = {
                    'patient': pid, 
                    'x': gtv[0], 'y': gtv[1], 
                    'baseX': gtv[0], 'baseY': gtv[1], 
                    'type': 'gtv',
                    'id': pid+'gtv',
                    'original': gtvPoints[i].map(toProximity),
                }
                allPoints.push(gtvPoint);
                link.source = gtvPoint.id
            }
            if(notAllZero(gtvnPoints[i])){
                let gtvnPoint = {
                    'patient': pid, 
                    'x': gtvn[0], 'y': gtvn[1], 
                    'baseX': gtvn[0], 'baseY': gtvn[1], 
                    'type': 'gtvn',
                    'id': pid+'gtvn',
                    'original': gtvnPoints[i].map(toProximity),
                }
                allPoints.push(gtvnPoint);
                link.target = gtvnPoint.id;
            }
            if(link.source !== undefined & link.target !== undefined){
                links.push(link);
            }
        }

        // console.log('allpoins',allPoints)

        const xScale = d3.scaleLinear()
            .domain(d3.extent(allPoints, d => d.x))
            .range([padding,width-padding]);

        const yScale = d3.scaleSymlog()
            .domain(d3.extent(allPoints, d => d.y))
            .range([height-padding,padding]);

        const proximityScale = d => d**.15;
        const getX = d => xScale(d.x);
        const getY = d => yScale(d.y);

        const getColor = d => {
            if(props.parameters.patientIDs.indexOf(parseInt(d.patient)) > -1){
                return d.type === 'gtv'? 'red': 'orange';
            }
            return 'grey';
        }
        const getOpacity = d => d.type === 'gtv'? 1:.8;
        const getRadius = d => 10;//d.type === 'gtv'? 10:6;

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
            .attr('transform',d => 'translate(' + getX(d) + ',' + getY(d) + ')')
            .attr('fill',getColor)
            .attr('stroke','black')
            .attr('stroke-width',1)
            .attr('fill-opacity',.95)
            .attr('stroke-opacity',1)
            .on('dblclick',function(e,d){
                if(props.parameters.patientIDs.indexOf(parseInt(d.patient)) > -1){
                    let newList = [parseInt(d.patient), props.selectedCloudIds[0]];
                    props.setSelectedCloudIds(newList)
                }
            })
            .on('mouseover',function(e,d){
                let string =d.patient + '-' + d.type + '</br>';
                for(let i in d.original){
                    string += colOrder[i] + ': ' + d.original[i].toFixed(3) + '</br>'; 
                }
                tTip.html(string);
            }).on('mousemove', function(e){
                Utils.moveTTipEvent(tTip,e);
            }).on('mouseout', function(e){
                Utils.hideTTip(tTip);
            });;

        const tick = ()=>{
            connections.attr('d',linkArc);
            svgPoints.attr('transform',d => 'translate(' + getX(d) + ',' + getY(d) + ')')
          }

        var simulation = d3.forceSimulation(allPoints)
            .alphaMin(.001)
            .force('collide',d3.forceCollide().radius(d=>getRadius(d)/2).strength(.05))
            .force('x', d3.forceX(d=>d.baseX).strength(1))
            .force('y',d3.forceY(d=>d.baseY).strength(1))
            .force('link',forceLink)
            .on('tick',tick);
    }

    function plotRadVis(data){
        console.log('radvis',data);
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

    return (
        <div
            className={"d3-component"}
            style={{'height':'95%','width':'95%'}}
            ref={d3Container}
        ></div>
    );
}