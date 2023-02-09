import React, {useState, useEffect, useRef} from 'react';
// import * as constants from "../modules/Constants.js";
import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js';
import * as d3 from 'd3';
import { cross } from 'd3';

function unravelDict(roiDict){
    let array = [];
    for(let [roi, entry] of Object.entries(roiDict)){
        if(entry.length < 1){continue}
        for(let value of entry){
            array.push({
                'value':value,
                'roi': roi,
            });
        }
    }   
    return array
}

function roiCentroid(roiDict,targetRoi){
    //technically this is actually the mode now
    //want to get the level with the most points
    if(roiDict[targetRoi] === undefined | roiDict[targetRoi].length < 3){
        console.log('missing roi entry in roiCentroid',targetRoi,Object.keys(roiDict));
        return {'x':0,'y':0,'z':0}
    }
    const points = roiDict[targetRoi];
    let centroid = [0,1,2].map(i => Utils.mode(points.map(d=>d[i])));
    centroid = {'x': centroid[0], 'y': centroid[1], 'z': centroid[2]};
    return centroid
}

export default function DicomSliceViewer(props){

    const d3Container = useRef(null);
    const [svg, height, width, tTip] = useSVGCanvas(d3Container);
    const epsilon = props.epsilon? props.epsilon:.5;
    const padding = 10;

    const cornerTextOptions = {
        'x': 'Side(L)',
        'z': 'Top(S)',
        'y': 'Front(A)'
    }

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(props.pCloudData)){
            svg.selectAll().remove();
            const pointPositions = unravelDict(props.pCloudData['contours']);
            const pointValues = unravelDict(props.pCloudData['contour_values']);
            const pId = props['id'];
            
            const brushedOrgan = props.brushedOrgan? props.brushedOrgan: 'GTVp';
            const crossSectionAxis = props.crossSectionAxis? props.crossSectionAxis:'z';
            const centroidOffset = props.brushHeight[crossSectionAxis] | 0;

            const centroid = roiCentroid(props.pCloudData['contours'],brushedOrgan);
            const pointGood = point => {
                return Math.abs(centroidOffset + centroid[crossSectionAxis] - point[crossSectionAxis]) <= epsilon;
            }
            var filteredPoints =[];
            for(let i in pointPositions){
                let pEntry = pointPositions[i];
                let vEntry = pointValues[i];
                let newEntry = {
                    'x': pEntry.value[0],
                    'y': pEntry.value[1],
                    'z': pEntry.value[2],
                    'roi': pEntry.roi,
                    'value': vEntry.value,
                }
                if(pointGood(newEntry)){
                    filteredPoints.push(newEntry);
                }
            }

            let getX = d => d.x;
            let getY = d => d.y;
            if(crossSectionAxis === 'x'){
                getX = d => -d.y;
                getY = d => d.z;
            } else if (crossSectionAxis == 'y'){
                getY = d => d.z;
            }


            const [xMin,xMax] = d3.extent(filteredPoints, getX);
            const [yMin, yMax] = d3.extent(filteredPoints, getY);
            const [minVal,maxVal] = d3.extent(filteredPoints, p => p.value);

            //if there are < 2000 points double the size?
            const xAspect = (width - 2*padding)/(xMax - xMin);
            const yAspect = (height - 2*padding)/(yMax - yMin);
            const pointRadius = .9*Math.min(xAspect, yAspect)
            // const pointRadius = ratio*((crossSectionAxis !== 'z') + 1)*Math.max(height,width)/300;
            const xScale = d3.scaleLinear()
                .domain([xMin, xMax])
                .range([padding, width-padding]);
            const yScale = d3.scaleLinear()
                .domain([yMin, yMax])
                .range([height-padding, padding]);
            const colorScale = d3.scaleLinear()
                .domain([minVal,maxVal])
                .range([.1,1]);
            const getColor = d => {
                let roi = d.roi;
                let interp = Utils.getRoiInterpolator(roi);
                let v = colorScale(d.value);
                return interp(v);
            }
            const getOpacity = d => d.roi === props.brushedOrgan? 1:.2;
            svg.selectAll('.pixel').remove();
            svg.selectAll('circle').filter('.pixel')
                .data(filteredPoints).enter()
                .append('circle').attr('class','pixel')
                .attr('cx', d=>xScale(getX(d)))
                .attr('cy', d => yScale(getY(d)))
                .attr('r',pointRadius)
                .attr('fill',getColor)
                .attr('opacity',getOpacity)
                .on('click',(e,d)=>{
                    const roi = d.roi;
                    if(roi !== undefined & roi !== brushedOrgan){
                        props.setBrushedOrgan(roi);
                    }
                }).on('mouseover',function(e,d){
                    tTip.html(d.roi);
                }).on('mousemove', function(e){
                    Utils.moveTTipEvent(tTip,e);
                }).on('mouseout', function(e){
                    Utils.hideTTip(tTip);
                });

            svg.selectAll('text').remove();
            let cornerText = Utils.getVarDisplayName(brushedOrgan) + '-' + cornerTextOptions[crossSectionAxis];
            cornerText += ' | Offset = ' + centroidOffset.toFixed(2) + 'mm';
            svg.append('text')
                .attr('class','legendText')
                .attr('x', padding)
                .attr('y', height - 5)
                .attr('text-anchor','start')
                .html(cornerText);

        }
    },[height,width,props.pCloudData,props.brushHeight[props.crossSectionAxis],props.brushedOrgan,props.crossSectionAxis]);

    return (
        <div
            className={"d3-component"}
            style={{'height':'95%','width':'95%'}}
            ref={d3Container}
        ></div>
    );
}