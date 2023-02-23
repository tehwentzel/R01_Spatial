import React, {useState, useEffect, useRef} from 'react';
// import * as constants from "../modules/Constants.js";
import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js';
import * as d3 from 'd3';

function makeItem(name, min=0,max=1){

    const scale = d3.scaleLinear()
        .domain([min,max])
        .range([.1,1]);
    return {'name': name, 'scale': d=> Math.max(Math.min(1,scale(d)),0)}
}

const stageMap = {
    't0': 0,
    'tx': 0,
    't1': 1,
    't2': 2,
    't3': 3,
    't4': 4,
    'n0': 0,
    'n1': 1,
    'n2': 2,
    'n2a': 2,
    'n2b': 2,
    'n2c': 2.5,
    'n3': 3,
}

export default function ClinicalGlyph(props){

    const d3Container = useRef(null);
    const [svg, height, width, tTip] = useSVGCanvas(d3Container);
    const padding = 10;
    const textSize = 10;
    const binaryItems = ['is_male','hpv','os','surgery_before_rt','BOT','Tonsil'];

    const ordinalItems = [
        makeItem('age',50,80),
        makeItem('t_stage',0,4),
        makeItem('n_stage',0,3)
    ];
    const plotItems = binaryItems.map(d=>makeItem(d,0,1)).concat(ordinalItems);

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(props.data)){
            const plotRadius = Math.min(height/2,width/2) - padding- 2*textSize;
            var pData = Object.assign({},props.data.data[props.patientId]);
            pData['BOT'] = + (pData.subsite === 'BOT');
            pData['Tonsil'] = + (pData.subsite === 'Tonsil');
            console.log(pData.n_stage)
            pData['t_stage'] = stageMap[pData.t_stage] !== undefined? stageMap[pData.t_stage]: 0;
            pData['n_stage'] = stageMap[pData.n_stage] !== undefined? stageMap[pData.n_stage]: 0;
            const symptoms = props.data.symptoms;
            const timePoints = props.data.timepoints;
            const arcLen = 2*Math.PI/plotItems.length;

            var nodes = [];
            var pathPoints = [];
            var currArc = -Math.PI/2; 
            for(let item of plotItems){
                let value = item.scale(parseFloat(+pData[item.name]));
                let [xOffset,yOffset] = Utils.radToCartesian(currArc, value*plotRadius);
                let [xTextOffset,yTextOffset] = Utils.radToCartesian(currArc, 2*textSize+plotRadius);
                let x = xOffset + width/2;
                let y = yOffset + height/2;
                let entry = {
                    x: x,
                    y: y,
                    xText: width/2 + xTextOffset,
                    yText: height/2 + yTextOffset,
                    name: item.name,
                    value: +pData[item.name],
                    theta: currArc,
                }
                nodes.push(entry);
                pathPoints.push([x,y]);
                currArc += arcLen;
            }
            pathPoints.push(pathPoints[0]);

            let arcFunc = d3.line();

            svg.selectAll('path').filter('.starPath').remove();
            svg.selectAll('path').filter('.starPath')
                .data([pathPoints]).enter()
                .append('path').attr('class','starPath')
                .attr('d',d=>arcFunc(d))
                .attr('stroke','black')
                .attr('stroke-width',3)
                .attr('fill','none');

            svg.selectAll('text').filter('.labelText').remove();
            svg.selectAll('text').filter('.labelText')
                .data(nodes).enter()
                .append('text').attr('class','labelText')
                .attr('x',d=>d.xText)
                .attr('y',d=>d.yText)
                .attr('text-anchor','middle')
                .text(d=>Utils.getVarDisplayName(d.name) + d.value)
                .attr('font-size',textSize)
        }
    },[height,width,props.data,props.patientId]);

    return (
        <div
            className={"d3-component"}
            style={{'height':'95%','width':'95%'}}
            ref={d3Container}
        ></div>
    );
}