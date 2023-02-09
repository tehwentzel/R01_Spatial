import React, {useState, useEffect, useRef} from 'react';
// import * as constants from "../modules/Constants.js";
import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js';
import * as d3 from 'd3';

export default function SpatialDoseGlyph(props){

    const d3Container = useRef(null);
    const [svg, height, width, tTip] = useSVGCanvas(d3Container);
    const [roiValues, setRoiValues] = useState({});
    const padding = 20;

    useEffect(()=>{
        if(height > 0 & width > 0 & Utils.validData(props.data) & Utils.validData(props.parameters)){
            
            const roiList = props.parameters.rois;
            
            if(roiList === undefined | props.brushedOrgan === undefined | props.data.distances === undefined){return}
            const centerRoi = props.brushedOrgan;
            const roiPos = roiList.indexOf(centerRoi);
            const dists = props.data.distances[roiPos];
            const proximities = dists.map(d => 1/(1+d))
            const maxRadius = (Math.min(width,height)/2) - padding;
            const minRadius = (Math.min(width,height)/5);
            const meanDoses = roiList.map(r => Utils.mean(props.data.contour_values[r]))
                .map(v => Number.isNaN(v)? 0: v);


            let entries = [];
            let arcLen = 2*Math.PI/roiList.length;
            let currRadialPos = 0;
            for(let i in roiList){
                let entry = {
                    'roi': roiList[i],
                    'dist': dists[i],
                    'proximity': proximities[i],
                    'meanDose': meanDoses[i],
                    'radialStart': currRadialPos,
                }
                entries.push(entry)
                currRadialPos += arcLen;
            }

            const doseScale = d3.scaleLinear()
                .domain(d3.extent(meanDoses))
                .range([.1,1]);

            const proximityScale = d3.scaleLinear()
                .domain([0,d3.max(proximities)])
                .range([minRadius,maxRadius]);

            const arcFunc = d3.arc()
                .innerRadius(d => proximityScale(0))
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

            const contourVals = props.data.contour_values[centerRoi]
            if(contourVals !== undefined & contourVals.length > 10){
                const quants = [.9,.8,.7,.6,.5,.4,.3,.2,.1];
                let dvh = quants.map(q => Utils.quantile(contourVals, q));
                let dvhScale = d3.scaleSymlog()
                    .domain(d3.extent(dvh))
                    .range([.1,minRadius-2]);
                let innerArcLen = 2*Math.PI/dvh.length;
                let currInnerArc = 0;
                let dvhEntries = dvh.map((dval,i)=> {
                    let entry = {
                        'value': dval,
                        'outerRadius': dvhScale(dval),
                        'radialStart': currInnerArc,
                        'color': d3.interpolateReds(dvhScale(dval)/minRadius),
                        'quantile': quants[i],
                    }
                    currInnerArc += innerArcLen;
                    return entry;
                })

                const innerArcFunc = d3.arc()
                    .innerRadius(.1)
                    .outerRadius(d=>d.outerRadius)
                    .startAngle(d=>d.radialStart)
                    .endAngle(d=>d.radialStart+innerArcLen);


                let innerArc = svg.selectAll('path').filter('.innerArc')
                    .data(dvhEntries);

                innerArc.exit().remove();

                if(innerArc.empty()){
                    innerArc.enter()
                        .append('path')
                        .attr('class','innerArc')
                        .attr('transform','translate(' + width/2 + ',' + height/2 + ')');
                }

                innerArc.enter().append('path')
                    .merge(innerArc).attr('class','innerArc') 
                    .on('mouseover',function(e,d){
                        tTip.html(props.brushedOrgan + ' V' + (100*(1-d.quantile)).toFixed(0) +': ' + d.value);
                    }).on('mousemove', function(e){
                        Utils.moveTTipEvent(tTip,e);
                    }).on('mouseout', function(e){
                        Utils.hideTTip(tTip);
                    });

                innerArc.exit().remove();

                innerArc.transition()
                    .duration(5000)
                    .attr('d',innerArcFunc)
                    .attr('fill',d=>d.color);

            } else{
                svg.selectAll('.innerArc').remove();
            }

            svg.selectAll('text').remove();
            let cornerText = Utils.getVarDisplayName(props.brushedOrgan) + ': inner=DVH, outer=organ distances';
            svg.append('text')
                .attr('class','legendText')
                .attr('x', width/2)
                .attr('y', height - 5)
                .attr('text-anchor','middle')
                .html(cornerText);
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