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
export default function SpatialDoseGlyph(props){

    const d3Container = useRef(null);
    const [svg, height, width, tTip] = useSVGCanvas(d3Container);
    const [roiValues, setRoiValues] = useState({});
    const padding = 10;

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(props.data) & (props.data.distances!==undefined) & Utils.validData(props.parameters)){
            console.log('glyph',props)
            return
            const distances = props.data.distances[0];
            //I think this was an accident but I save all the good organs instead of doign 0 if it's missing
            const distance_organs = props.data.distances[1];
            const roiList = props.parameters.rois;
            const centerRoi = getValidOrgan(distances,props.brushedOrgan);
            if(centerRoi === 'none'){
                console.log('glyph bad',distances,props.brushedOrgan);
                return;
            }

            // console.log('glyph good',distances,centerRoi);
            
            const roiPos = roiList.indexOf(centerRoi);

            const dists = distances[centerRoi];
            console.log()
            const proximities = dists.map(d => 1/(1+d))
            const maxRadius = (Math.min(width,height)/2) - padding;
            const innerRadius =  Math.min(width,height)/20;
            const minRadius = maxRadius/2;
            const getMeanDose = r => {
                let entry = props.data.point_clouds[r];
                if(entry == undefined){
                    return 0;
                }
                let val = Utils.mean(entry.dose_values);
                return Number.isNaN(val)? 0: val;
            }
            const meanDoses = roiList.map(getMeanDose);


            let entries = [];
            let arcLen = 2*Math.PI/roiList.length;
            let currRadialPos = 0;
            for(let i in roiList){
                let r = roiList[i];
                let di = distance_organs.indexOf(r);
                let idist = di < 0? 0:dists[di];
                let iprox = di < 0? 0:proximities[di];
                let entry = {
                    'roi': r,
                    'dist': idist,
                    'proximity': iprox,
                    'meanDose': meanDoses[i],
                    'radialStart': currRadialPos,
                }
                entries.push(entry)
                currRadialPos += arcLen;
            }

            const doseScale = d3.scaleLinear()
                .domain(d3.extent(meanDoses))
                .range([.1,1]);

            const proximityScale = d3.scaleSymlog()
                .domain([0,d3.max(proximities)])
                .range([minRadius,maxRadius]);

            const arcFunc = d3.arc()
                .innerRadius(d=>proximityScale(0)/2)
                .outerRadius(d => proximityScale(d.proximity))
                .startAngle(d => d.radialStart)
                .endAngle(d => d.radialStart + arcLen);

            const getColor = d => {
                let interp = Utils.getRoiInterpolator(d.roi);
                return interp(doseScale(d.meanDose));
            }



            let arcs = svg.selectAll('.arc').data(entries);
            arcs.exit().remove();
            if(arcs.empty()){
                arcs.enter().append('path')
                .attr('class','arc')
                .attr('stroke','black')
                .attr('transform','translate(' + width/2 + ',' + height/2 + ')');
                
            }

            arcs.enter().append('path')
                .merge(arcs)
                .attr('class','arc')
                .on('dblclick',(e,d)=>{
                    const roi = d.roi;
                    if(roi !== undefined & roi !== props.brushedOrgan){
                        props.setBrushedOrgan(roi);
                    }
                }).on('mouseover',function(e,d){
                    tTip.html(d.roi + '</br> dist: ' + d.dist.toFixed(1) + '</br> mean Value: ' + d.meanDose.toFixed(1));
                }).on('mousemove', function(e){
                    Utils.moveTTipEvent(tTip,e);
                }).on('mouseout', function(e){
                    Utils.hideTTip(tTip);
                });
                
            arcs.exit().remove();
            arcs.transition()
                .duration(5000)
                .attr('d',arcFunc)
                .attr('stroke-width', d=> d.roi === props.brushedOrgan? 1:0)
                .attr('fill',getColor);

        }
    },[height,width,props.data,props.brushedOrgan]);

    return (
        <div
            className={"d3-component"}
            style={{'height':'95%','width':'95%'}}
            ref={d3Container}
        ></div>
    );
}