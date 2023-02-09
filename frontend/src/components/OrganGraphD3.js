import React, {useState, useEffect, useRef} from 'react';
// import * as constants from "../modules/Constants.js";
import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js';
import * as d3 from 'd3';

function roiCentroid2D(roiDict,targetRoi){
    if(roiDict[targetRoi] === undefined | roiDict[targetRoi].length < 3){
        return {'x':0,'y':0,'id':targetRoi}
    }
    const points = roiDict[targetRoi];
    let centroid = [0,1].map(i => Utils.median(points.map(d=>d[i])))
    centroid = {'x': centroid[0], 'y': centroid[1],'id':targetRoi};
    return centroid
}

export default function OrganGraphD3(props){

    const d3Container = useRef(null);
    const [svg, height, width, tTip] = useSVGCanvas(d3Container);
    const [centroids, setCentroids] = useState({});
    const [roiValues, setRoiValues] = useState({});
    const radius = 10;
    const padding = 4*radius;
    const minDist = 10;//minimum distance to show the links

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(props.data) & Utils.validData(props.parameters)){
            const roiList = props.parameters.rois;
            const c = roiList.map(r => roiCentroid2D(props.data.contours,r));
            const v = roiList.map(r => Utils.mean(props.data.contour_values[r]))
                .map(v => Number.isNaN(v)? 0: v);
            setCentroids(c);
            setRoiValues(v);
        } 
    },[svg,props.data,props.parameters])

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(centroids)){
            svg.selectAll('circle').remove();
            
            const roiList = props.parameters.rois;
            const centerRoi = props.brushedOrgan !== undefined? props.brushedOrgan: 'GTVp';
            var rPos = roiList.indexOf(props.brushedOrgan);
            if(rPos < 0){
                rPos = 0;
            }

            const xLims = d3.extent(centroids, d=>d.x);
            const yLims = d3.extent(centroids, d=>d.y);

            const xScale = d3.scaleLinear()
                .domain(xLims)
                .range([padding,width-padding]);
            const yScale = d3.scaleLinear()
                .domain(yLims)
                .range([height-padding,padding]);

            const dists = props.data.distances[rPos];


            const volumes = props.data.Volumes;
            const maxVolume = d3.max(volumes);
            const nodes = centroids.map(d => {
                let pos = roiList.indexOf(d.id)
                return {
                    'id':d.id,
                    'x':xScale(d.x),
                    'y':yScale(d.y),
                    'baseY': yScale(d.y),
                    'baseX': xScale(d.x),
                    'distance': dists[pos],
                    'volume': volumes[pos],
                    'value': roiValues[pos],
                }
            });

            
            var links = roiList.map((d,i) => {return {source: centerRoi, target: d,distance: dists[i]}})
                .filter(d=> d.source !== d.target);


            var showLinks = links.filter(d => d.distance < minDist);
            const dScale = d3.scalePow(.5)
                .domain(d3.extent(showLinks,d=>d.distance))
                .range([1,.1]);
            const getStroke = d => 3*dScale(d.distance)
            svg.selectAll('path').filter('.linkLine').remove();
            var lines = svg.selectAll('path')
                .filter('.linkLine')
                .data(showLinks)
                .enter().append('path')
                .attr('class','linkLine')
                .attr('fill','none')
                .attr('stroke-width',getStroke)
                .attr('stroke','black');

            const active = d => d.id === centerRoi;
            const getRadius = (d) =>{
                let r = radius*((d.volume/maxVolume)**.25);
                if(active(d)){
                    r *= 1.2;
                }
                return r
            }

            const colorScale = d3.scaleLinear()
                .domain(d3.extent(roiValues))
                .range([.5,1]);
            const interpolator = Utils.getRoiInterpolator
            var getColor = d => {
                let interp = Utils.getRoiInterpolator(d.id);
                return interp(colorScale(d.value));
            }
            var nodeObj = svg.selectAll('circle')
                .data(nodes).enter()
                .append('circle')
                .attr('r',getRadius)
                .attr('fill',getColor)
                .attr('stroke','blue')
                .attr('stroke-width', d=> active(d)? 3:0)
                .attr('cx',d=>d.x)
                .attr('cy',d=>d.y)
                .on('click',(e,d)=>{
                    const roi = d.id;
                    if(roi !== undefined & roi !== props.brushedOrgan){
                        props.setBrushedOrgan(roi);
                    }
                }).on('mouseover',function(e,d){
                    tTip.html(d.id + '</br> distance: ' + d.distance + '</br> volume: ' + d.volume);
                }).on('mousemove', function(e){
                    Utils.moveTTipEvent(tTip,e);
                }).on('mouseout', function(e){
                    Utils.hideTTip(tTip);
                });


            var forceLink = d3.forceLink()
                .id(d=>d.id)
                .distance((d,i)=>3*dists[i])
                .strength(.5)
                .links(links);

            const lineFunc = d3.line();
            const linkArc = d => lineFunc([[d.source.x,d.source.y],[d.target.x,d.target.y]]);

            function ticked() {
                svg.selectAll('path').filter('.linkLine').attr('d',linkArc);
                svg.selectAll('circle').attr('cx',d=>d.x).attr('cy',d=>d.y);
            }
            const fStrength = 1;
            var simulation = d3.forceSimulation(nodes)
                .force('link',forceLink)
                .force('x',d3.forceX(d=>d.baseX).strength(fStrength))
                .force('y',d3.forceY(d=>d.baseY).strength(fStrength))
                .force('collide',d3.forceCollide().radius(getRadius).strength(1))
                .force('center',d3.forceCenter(width/2,height/2).strength(.1))
                .on('tick',ticked);
            
        }
    },[height,width,centroids,props.brushedOrgan,roiValues]);

    return (
        <div
            className={"d3-component"}
            style={{'height':'95%','width':'95%'}}
            ref={d3Container}
        ></div>
    );
}