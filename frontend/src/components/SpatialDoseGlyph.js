import React, {useState, useEffect, useRef} from 'react';
// import * as constants from "../modules/Constants.js";
import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js';
import * as d3 from 'd3';

function getValidOrgan(obj, organ){
    const defaults = ['gtv','gtvn']
    if(obj[organ] !== undefined){
        return organ;
    } 
    for(let o of defaults){
        if(obj[o] !== undefined){ return o}
    }
    return 'none'
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

export default function SpatialDoseGlyph(props){

    const d3Container = useRef(null);
    const [svg, height, width, tTip] = useSVGCanvas(d3Container);
    const [roiValues, setRoiValues] = useState({});
    const padding = 10;
    const centerColor = 'blue';

    function toProximity(d){
        if(d === 0 | d >= 10000000){
            return 0;
        }
        return 1/1+d;
    }

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(props.distanceData) & Utils.validData(props.patientData)){
            const pid = props.patientData.patient_id;
            const distances = props.distanceData.distances[pid];
            if(distances === undefined){
                console.log('missing',pid,Object.keys(props.distanceData.distances));
                return
            }
            
            const rowNames = props.distanceData.rowOrder;
            const colNames = props.distanceData.colOrder;

            // const centerRoi = 'gtv';
            // const roiPos = rowNames.indexOf(centerRoi);
            const mainDists = distances[rowNames.indexOf('gtv')];
            const nodeDists = distances[rowNames.indexOf('gtvn')];
            const dists = notAllZero(mainDists)? mainDists: nodeDists;
            const mainRoi = notAllZero(mainDists)? 'gtv': notAllZero(nodeDists)? 'gtvn':'gtvn';
            const proximities = dists.map(toProximity)
            const maxRadius = (Math.min(width,height)/2) - padding;
            const innerRadius =  5;
            const minRadius = 20;


            let entries = [];
            let arcLen = 2*Math.PI/colNames.length;
            let currRadialPos = 0;
            for(let i in colNames){
                let entry = {
                    'roi': colNames[i],
                    'dist': dists[i],
                    'proximity': proximities[i],
                    'radialStart': currRadialPos,
                }
                entries.push(entry)
                currRadialPos += arcLen;
            }

            const proximityScale = d3.scaleSymlog()
                .domain([0,d3.max(entries, d=> d.proximity)])
                .range([minRadius,maxRadius]);

            const colorScale = d3.scaleLinear()
                .domain([0,d3.max(proximities)])
                .range([0.1,.9]);

            const arcFunc = d3.arc()
                .innerRadius(innerRadius)
                .outerRadius(d => proximityScale(d.proximity))
                .startAngle(d => d.radialStart)
                .endAngle(d => d.radialStart + arcLen);

            const getColor = d => d3.interpolateGreys(colorScale(d.proximity))


            let center = svg.append('circle')
                .attr('class','centerCircle')
                .attr('cx', width/2)
                .attr('cy',height/2)
                .attr('r',innerRadius)
                .attr('fill',centerColor)
                .on('dblclick',()=>{
                    if(props.brushedOrgan != mainRoi){
                        props.setBrushedOrgan(mainRoi);
                    }
                })
            // console.log('entreis',entries)
            let arcs = svg.selectAll('path').filter('.arc')
                .data(entries).enter().append('path')
                .attr('d',arcFunc)
                .attr('class','arc')
                .attr('stroke','black')
                .attr('transform','translate(' + width/2 + ',' + height/2 + ')')
                .attr('stroke-width', d=> d.roi === props.brushedOrgan? 1:0)
                .attr('fill',getColor)
                .on('dblclick',(e,d)=>{
                    const roi = d.roi;
                    if(roi !== undefined & roi !== props.brushedOrgan){
                        props.setBrushedOrgan(roi);
                    }
                }).on('mouseover',function(e,d){
                    tTip.html(d.roi + '</br> dist: ' + d.dist.toFixed(1));
                }).on('mousemove', function(e){
                    Utils.moveTTipEvent(tTip,e);
                }).on('mouseout', function(e){
                    Utils.hideTTip(tTip);
                });

            // arcs.exit().remove();
            // if(arcs.empty()){
            //     arcs.enter().append('path')
            //     .attr('class','arc')
            //     .attr('stroke','black')
            //     .attr('transform','translate(' + width/2 + ',' + height/2 + ')');
                
            // }

            // arcs.enter().append('path')
            //     .merge(arcs)
            //     .attr('class','arc')
            //     .on('dblclick',(e,d)=>{
            //         const roi = d.roi;
            //         if(roi !== undefined & roi !== props.brushedOrgan){
            //             props.setBrushedOrgan(roi);
            //         }
            //     }).on('mouseover',function(e,d){
            //         tTip.html(d.roi + '</br> dist: ' + d.dist.toFixed(1));
            //     }).on('mousemove', function(e){
            //         Utils.moveTTipEvent(tTip,e);
            //     }).on('mouseout', function(e){
            //         Utils.hideTTip(tTip);
            //     });

            // arcs.exit().remove();
            // arcs.transition()
            //     .duration(5000)
            //     .attr('d',arcFunc)
            //     .attr('stroke-width', d=> d.roi === props.brushedOrgan? 1:0)
            //     .attr('fill',getColor);

        }
    },[height,width,props.distanceData,props.patientData,props.brushedOrgan]);

    return (
        <div
            className={"d3-component"}
            style={{'height':'95%','width':'95%'}}
            ref={d3Container}
        ></div>
    );
}