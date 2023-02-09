import React, {useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';
// import useSVGCanvas from './useSVGCanvas.js';
import Utils from '../modules/Utils.js'
import * as THREE from 'three';
// import { Scene, StereoCamera } from 'three';
// import {Canvas, useThree, useFrame} from '@react-three/fiber'
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls';



function getRenderer(){
    var r = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true
    });
    r.setClearColor(0xFFFFFF, 1);
    r.setPixelRatio(window.devicePixelRatio);
    r.sortObjects = true;
    return r;
}

function getCameraCoords(coords,camera){
    let pos = new THREE.Vector3(coords[0],coords[1],coords[2]);
    camera.updateMatrixWorld();
    pos.project(camera);
    return [pos.x,pos.y,pos.z]
}

export default function DicomPointCloudViz(props){
    const mountRef = useRef(null);
    const [height, setHeight] = useState(0);
    const [width, setWidth] = useState(0);
    const [renderer, setRenderer] = useState();
    const[camera, setCamera] = useState();
    const [scene, setScene] = useState();
    const [controls, setControls] = useState();
    const [tTip, setTTip] = useState();

    const pointSize = 10;
    const cameraDist=500;
    const mouseVector = new THREE.Vector2(-500, -500);
    const mouse = new THREE.Vector2(-500,500);
    const cameraSyncInterval = 50;
    const sceneScale = 2.5;

    const brushedOpacity = 1;
    const unbrushedOpacity = .5;

    const nodeSize = 15;
    const nodeColor = new THREE.Color().setHex(0xa0a0a0);
    
    const getCenter = v => (v[1] + v[0])/2;
    function makeCentroid(roi, roiPoints){

        let centroid = [0,1,2].map(i => 2*Utils.median(roiPoints.map(d=>d[i])));
        centroid = new THREE.Vector3(...centroid);
        var material = new THREE.MeshBasicMaterial({color:nodeColor,opacity:.5,transparent:true});
        var geo = new THREE.SphereGeometry(nodeSize,16);
        
        let organSphere = new THREE.Mesh(geo,material);
        // organSphere.position.set(centroid);
        organSphere.position.x = centroid.x;
        organSphere.position.y= centroid.y;
        organSphere.position.z = centroid.z;
        organSphere.userData.type = 'organNode';
        organSphere.userData.organName = roi;
        return organSphere;
    }

    function getPointGeom(data){
        // if(!Utils.validData(data)){return false}
        
        const pointPositions = data['contours'];
        const pointValues = data['contour_values'];
        const pId = props['id'];

        var verts = [];
        var rois = [];
        var vals = [];
        var centroids = [];
        for(const [key, roiPoints] of Object.entries(pointPositions)){
            // if(!key.includes('sterno')){continue}
            if(roiPoints === undefined | roiPoints.length < 3){ continue; }
            const centroidMesh = makeCentroid(key,roiPoints);
            centroids.push(centroidMesh);
            const roiPointVals = pointValues[key];
            for(let i in roiPoints){
                let coord = roiPoints[i];
                let val = roiPointVals[i];
                if(coord.length == 3){
                    verts.push(...coord.map(d=>2*d));
                    rois.push(key);
                    vals.push(val);
                }else{
                    console.log('bad',coord)
                }
            }
        }
        let colorScale = d3.scaleLinear()
            .domain([0,d3.max(vals)])
            .range([.5,1]);
        let colors = [];
        for(let i in vals){
            let val = vals[i];
            let roi = rois[i];
            let interp = roi.includes("GTV")? d3.interpolateReds:d3.interpolatePuBu;
            let c = interp(colorScale(val));
            c  = d3.color(c);
            let alpha = (roi === props.brushedOrgan)? brushedOpacity:unbrushedOpacity;
            c = [c.r/255, c.g/255, c.b/255, alpha];
            colors.push(...c);
        }

        verts = new THREE.BufferAttribute(new Float32Array(verts),3);
        colors = new THREE.BufferAttribute(new Float32Array(colors),4);
        verts.name = 'pointCloudVertices';
        colors.name = 'pointCloudColors';
        var geometry = new THREE.BufferGeometry();
        geometry.setAttribute( 'position', verts);
        geometry.setAttribute( 'color', colors);
        var material = new THREE.PointsMaterial({vertexColors: true,size: 2,transparent:true});
        var pointCloud = new THREE.Points(geometry,material);
        pointCloud.userData.type = 'pointcloud';
        // for(let centroidMesh of centroids){
        //     pointCloud.add(centroidMesh);
        // }
        return [pointCloud];

    }

    

    useEffect( () => {
        //wait for mounting to calculate parent container size
        if(!mountRef.current){ return; }
        var h = mountRef.current.clientHeight*.99;
        var w = mountRef.current.clientWidth;

        if(d3.select('.tooltip').empty()){
            d3.select('body').append('div')
                .attr('class','tooltip')
                .style('visibility','hidden');
        }
        var tip = d3.select('.tooltip');

        setHeight(h);
        setWidth(w);
        setTTip(tip);
        // console.log("height widht",h,w)
    },[mountRef.current]);

    useEffect( () => {
        //setup camera
        if(width <= 0 || height <= 0){ return; }

         //how big the head is relative to the scene 2 is normal;
        var camera = new THREE.OrthographicCamera(
            -width/sceneScale,
            width/sceneScale,
            height/sceneScale,
            -height/sceneScale,
            1, 1000);
        camera.position.z = props.cameraPositionZ;

        // orientation marker, patient coordinate system
        const boxSize = Utils.min(height,width)/7;
        var MovingCubeGeom = new THREE.BoxGeometry(boxSize,boxSize,boxSize, 1, 1, 1, props.materialArray);
        //cube mesh needs to be rotated to be in the correct order
        MovingCubeGeom.rotateX(Math.PI/2);
        var MovingCube = new THREE.Mesh(MovingCubeGeom, props.materialArray);
        MovingCube.position.set(width/2 - 2*boxSize, -height/2 + 2*boxSize,-props.cameraPositionZ);
        MovingCube.name = "orientationCube";
        MovingCube.renderOrder = 1;
        camera.add(MovingCube);
        
        var renderer = getRenderer();
        renderer.setSize(width, height)
        mountRef.current.appendChild(renderer.domElement);


        setRenderer(renderer);
        setCamera(camera);
    },[height, width]);
    
    useEffect(()=>{
        if(!renderer){return}
        var newScene = new THREE.Scene();
        camera.updateProjectionMatrix();
        newScene.add(camera);

        var controls = new OrbitControls(camera, renderer.domElement);
        controls.minDistance = 1;
        controls.maxDistance = 5000;
        controls.enablePan = false;
        // controls.enableZoom = false;

        if(Utils.validData(props.data)){
            const pointClouds = getPointGeom(props.data);
            for(let p of pointClouds){
                newScene.add(p);
            }
            // const centroidMeshes = getPointCentroids(props.data);
            // for(let c of centroidMeshes){
            //     newScene.add(c);
            // }
        }
        setScene(newScene);
        setControls(controls);
    },[renderer,props.data,props.brushedOrgan])

    useEffect(() => {
        //update camera position based on selected camera
        const interval = setInterval(() => {
          if(camera !== undefined & props.mainCamera !== undefined & scene !== undefined){
            camera.position.subVectors(props.mainCamera.position,controls.target);
            camera.lookAt(scene.position);
          }
        }, cameraSyncInterval);
        return () => clearInterval(interval);
    }, [renderer, scene, camera,props.mainCamera]);

    useEffect(() => {
        //update camera position based on selected camera
        const interval = setInterval(() => {
          if(camera !== undefined & props.mainCamera !== undefined & scene !== undefined){
            camera.position.subVectors(props.mainCamera.position,controls.target);
            camera.lookAt(scene.position);
          } 
        }, cameraSyncInterval);
        return () => clearInterval(interval);
    }, [renderer, scene, camera,props.mainCamera]);



    useEffect(() => {
        //main animate loop
        if(!renderer || !scene || !camera){ 
            // console.log('missing stuff for animate loop',renderer, scene,camera)
            return; 
        }
        let animate = function () {
            requestAnimationFrame( animate );
            renderer.clear();

            if(controls){
                var rotMatrix = new THREE.Matrix4();
                rotMatrix.extractRotation(controls.object.matrix);

                var orientationCube = camera.getObjectByName("orientationCube");
                orientationCube.rotation.setFromRotationMatrix(rotMatrix.transpose());
            }

            renderer.render( scene, camera );
        }
    
        animate();
    },[renderer, scene, camera,props.mainCamera,props.brushedOrganName]);


    useEffect(() => {
        return () => {
            if(!renderer){return;}
            renderer.forceContextLoss();
        }
    },[renderer]);

    const handleMouseDown = function(){
        //when you click on the item, make this the camera you sync to
        if(camera !== undefined){
            props.setMainCamera(camera);
        }
    }

    const handleMouseMove = (e)=>{
        //track mousemovement?
        if(width <= 0 || height <= 0){return;}
        if(e.target){
            //I need a sperate thing for raycasting according to stack exchange?
            mouseVector.x = (e.nativeEvent.offsetX / width) * 2 - 1;
            mouseVector.y = -(e.nativeEvent.offsetY / height) * 2 + 1;
            mouse.x = e.nativeEvent.clientX;
            mouse.y = e.nativeEvent.clientY;

            if(scene){
                props.raycaster.setFromCamera(mouseVector,camera);
                var intersects = props.raycaster.intersectObjects(scene.children);
                var intersected = false;
                if(intersects.length >= 1){
                    for(let i of intersects){
                        let obj = i.object;
                        //currently I can only check if I'm intersecting with the 
                        //whole pointcloud or not
                        
                        if(obj.userData.type === "organNode"){
                            console.log(obj)
                            Utils.moveTTip(tTip, mouse.x,mouse.y);
                            tTip.html(obj.userData.organName);
                            if(obj.userData.organName !== undefined){
                                props.setBrushedOrgan(obj.userData.organName)
                            }
                            intersected = true;
                            break;
                        } 
                    }
                }
                if(!intersected){
                    Utils.hideTTip(tTip);
                } 
            }
        }
    };

    return (
        <div ref={mountRef} className={'fillSpace'} 
        onMouseDown={handleMouseDown}
        onClick={handleMouseMove}
        >
        </div>
    )


}
