import React, {useState, useEffect, useRef} from 'react';
// import * as constants from "../modules/Constants.js";
import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js';
import * as d3 from 'd3';

const concaveman = require('concaveman');

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

function getCentroidZ(points,offset){
    //technically this is actually the mode now
    //want to get the level with the most points
    var levels = [... new Set(points)];
    var centroid = Utils.mode(points);
    offset = parseInt(offset);
    if(offset != 0){
        levels.sort()
        let index = levels.indexOf(centroid);
        index = Math.min(index + offset,levels.length);
        index = Math.max(index, 0)
        return levels[index];
    }
    return centroid
}

function getValidOrgan(pc, organ){
    const defaults = ['gtv','gtvn','ctv','ptv']
    if(pc[organ] !== undefined){
        return organ;
    } 
    for(let o of defaults){
        if(pc[o] !== undefined){ return o}
    }
    return 'none'
}
export default function DicomSliceViewer(props){

    const d3Container = useRef(null);
    const [svg, height, width, tTip] = useSVGCanvas(d3Container);
    const epsilon = 0;//props.epsilon? props.epsilon: 0;//thickness of the crossesction, can be 0 since we used mode for the center
    const padding = 10;
    const defaultSpacing = [2.75,2.5,2.75];//pixel spacing, currentyl using trial and eror

    const skipRois = ['oral_cavity']
    const cornerTextOptions = {
        'x': 'Side(L)',
        'z': 'Top(S)',
        'y': 'Front(A)'
    }
    const coordIndex = {
        'x': 0,
        'y': 1,
        'z': 2,
    }

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(props.pCloudData)){
            svg.selectAll().remove();

            // return
            const pointClouds = props.pCloudData['contour_pointclouds'];
            const contours = props.pCloudData['contours'];
            const brushedOrgan = getValidOrgan(pointClouds,props.brushedOrgan);
            const spacing = props.pCloudData.spacing === null? defaultSpacing: props.pCloudData.spacing;
            if(brushedOrgan === 'none'){
                console.log('no valid brushed organ');
                return;
            }
            const crossSectionAxis = props.crossSectionAxis? props.crossSectionAxis:'z';
            const centroidOffset = props.offset;

            const sliceAxisIndex = coordIndex[crossSectionAxis];
            const roiCentroid = getCentroidZ(pointClouds[brushedOrgan].coordinates.map( d => d[sliceAxisIndex]),centroidOffset) 
            // Utils.mode(pointClouds[brushedOrgan].coordinates.map( d => d[sliceAxisIndex]));
            const pointGood = (point,eps) => {
                return Math.abs(roiCentroid - point[sliceAxisIndex]) <= eps;
            }

            let getX = d => d.x;
            let getY = d => d.y;
            let getZ = d => d.z;
            let pixelSize = [spacing[0],spacing[1]];
            if(crossSectionAxis === 'x'){
                getX = d => -d.y;
                getY = d => d.z;
                getZ = d => -d.x;
                pixelSize = [spacing[1],spacing[2]];
            } else if (crossSectionAxis == 'y'){
                getY = d => d.z;
                getZ = d => d.y
                pixelSize = [spacing[0],spacing[2]];
            }

            var filteredPoints =[];
            var paths = [];
            const pId = props['patient_id'];
            //todo: I think I can speed tis up
            for(const [roi,entry] of Object.entries(pointClouds)){
                if(skipRois.indexOf(roi) > -1){ continue}
                // if(roi.includes('ptv') | roi.includes('ctv')){continue}

                //the commented stuff is an attempt at speeding up that doesnt work
                let values = entry['dose_values'].map(d=>d);
                //idk how else to preserve the sort order when soring valus
                let coordinates = entry['coordinates'].map(d=>d);
                let roiPoints =[];
                for(let i in coordinates){
                    if(pointGood(coordinates[i],epsilon)){
                        let point = coordinates[i];
                        let value = values[i];
                        let newEntry = {
                            'x': point[0],
                            'y': point[1],
                            'z': point[2],
                            'roi': roi,
                            'value': value,
                            'active': roi === brushedOrgan,
                        }
                        filteredPoints.push(newEntry)
                        roiPoints.push(newEntry)
                    } 
                    
                }
                //contours based on pointclouds, coordinates make it weird if not in z axis
                //maybe useful for testing if they align correctly
                // let roiContours = contours[roi];
                // for(let c of roiContours){
                //     console.log('c',c,c[0])
                //     let cdists = c.map( point => Math.abs(centroidOffset + roiCentroid - point[sliceAxisIndex]));
                //     let minD = Math.min(...cdists);
                //     c = c.filter((d,i) => cdists[i] <= minD);
                //     if(c.length > 4){
                //         let cpoints = c.map(d => {return {'x': d[0],'y': d[1],'z': d[2]}})
                //         let edges = cpoints.map(d=> [getX(d),getY(d)]);
                //         paths.push({points:edges, roi: roi});
                //     }
                // }

                //calculate the concave hull around each set of stuff
                // if(roi.includes('gtv') | roi == brushedOrgan){
                    if(roiPoints.length > 10 & !roi.includes('ptv') & !roi.includes('ctv') ){
                        const edges = concaveman(roiPoints.map(d=> [getX(d),getY(d)]));
                        paths.push({'points': edges,'roi': roi});
                    }
                // }
            }
            // console.log('filteredpoins',paths);

            //this is for rendering purposes: show stuff on top that is on top
            if(epsilon > 0){
                filteredPoints.sort((a,b) => a[crossSectionAxis] - b[crossSectionAxis]);
            }
            
            


            const [xMin,xMax] = d3.extent(filteredPoints, getX);
            const [yMin, yMax] = d3.extent(filteredPoints, getY);
            const [minVal,maxVal] = d3.extent(filteredPoints, p => p.value);

            //if there are < 2000 points double the size?
            const xAspect = (width - 2*padding)/(xMax - xMin);
            const yAspect = (height - 2*padding)/(yMax - yMin);
            const pixelWidth = xAspect*pixelSize[0];
            const pixelHeight = yAspect*pixelSize[1];
            const aspect = Math.min(xAspect, yAspect);
            const pointRadius = ((width*height)/Math.sqrt(filteredPoints.length))/500;
            // const pointRadius = ratio*((crossSectionAxis !== 'z') + 1)*Math.max(height,width)/300;
            const xScale = d3.scaleLinear()
                .domain([xMin, xMax])
                .range([padding, width-padding]);
            const yScale = d3.scaleLinear()
                .domain([yMin, yMax])
                .range([height-padding, padding]);
            const arcFunc = d3.line().curve(d3.curveBasisClosed)
                .x(d => xScale(d[0]))
                .y(d => yScale(d[1]));
            const colorScale = d3.scalePow(1)
                .domain([0,maxVal])
                .range([0,1]);
            const getColor = d => {
                let roi = d.roi;
                let interp = Utils.getRoiInterpolator(roi);
                let v = colorScale(d.value);
                return interp(v);
            }
            const getOpacity = d => {
                if(d.roi === props.burshedOrgan){
                    return 1
                }else{
                    let tumors = ['gtv','gtvn']
                    let supplement = ['ctv','ptv'];
                    return tumors.indexOf(d.roi) > -1? .9: supplement.indexOf(d.roi) > -1? .4:.8;
                }
                return .25;
            }
            svg.selectAll('.pixel').remove();

            //im testing squares or rectangles idk
            svg.selectAll('rect').filter('.pixel')
                .data(filteredPoints).enter()
                .append('rect').attr('class',d => d.active? 'pixel activePixel':'pixel')
                .attr('x', d=>xScale(getX(d))-pixelWidth/2)
                .attr('y', d => yScale(getY(d))-pixelWidth/2)
                .attr('height',pixelWidth)
                .attr('width',pixelWidth)
                .attr('fill',getColor)
                .attr('shape-rendering','optimizeQuality')
                .attr('stroke-width',0)
                .attr('stroke','black')
                .attr('opacity',getOpacity)
                .on('click',(e,d)=>{
                    const roi = d.roi;
                    if(roi !== undefined & roi !== brushedOrgan){
                        props.setBrushedOrgan(roi);
                    }
                }).on('mouseover',function(e,d){
                    let text = d.roi + '</br>' + d.value;
                    text += '</br>z-index' + getZ(d);
                    tTip.html(text);
                }).on('mousemove', function(e){
                    Utils.moveTTipEvent(tTip,e);
                }).on('mouseout', function(e){
                    Utils.hideTTip(tTip);
                });

            svg.selectAll('.activePixel').raise();

            // svg.selectAll('circle').filter('.pixel')
            //     .data(filteredPoints).enter()
            //     .append('circle').attr('class','pixel')
            //     .attr('cx', d=>xScale(getX(d)))
            //     .attr('cy', d => yScale(getY(d)))
            //     .attr('r',pointRadius)
            //     .attr('fill',getColor)
            //     .attr('opacity',getOpacity)
            //     .on('click',(e,d)=>{
            //         const roi = d.roi;
            //         if(roi !== undefined & roi !== brushedOrgan){
            //             props.setBrushedOrgan(roi);
            //         }
            //     }).on('mouseover',function(e,d){
            //         tTip.html(d.roi + '</br>' + d.value);
            //     }).on('mousemove', function(e){
            //         Utils.moveTTipEvent(tTip,e);
            //     }).on('mouseout', function(e){
            //         Utils.hideTTip(tTip);
            //     });

            svg.selectAll('path').filter('.organOutline').remove();
            svg.selectAll('path').filter('.organOutline')
                .data(paths).enter()
                .append('path').attr('class','organOutline')
                .attr('d',d=>arcFunc(d.points))
                .attr('fill-opacity',0)
                .attr('fill','none')
                .attr('stroke-width',d => d.roi.includes('gtv') | (d.roi === props.brushedOrgan)? 3:1)
                .attr('stroke', d=> Utils.getRoiInterpolator(d.roi)(1))
                .on('mouseover',function(e,d){
                    tTip.html(d.roi);
                }).on('mousemove', function(e){
                    Utils.moveTTipEvent(tTip,e);
                }).on('mouseout', function(e){
                    Utils.hideTTip(tTip);
                });;

            // svg.selectAll('text').remove();
            // let cornerText = Utils.getVarDisplayName(brushedOrgan) + '-' + cornerTextOptions[crossSectionAxis];
            // cornerText += ' | Offset = ' + centroidOffset.toFixed(2) + 'mm';
            // svg.append('text')
            //     .attr('class','legendText')
            //     .attr('x', padding)
            //     .attr('y', height - 5)
            //     .attr('text-anchor','start')
            //     .html(cornerText);

        }
    },[height,width,props.pCloudData,props.offset,props.brushedOrgan,props.crossSectionAxis]);

    return (
        <div
            className={"d3-component"}
            style={{'height':'95%','width':'95%'}}
            ref={d3Container}
        ></div>
    );
}