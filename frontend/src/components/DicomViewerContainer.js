import React, {useState, useEffect, useRef} from 'react';
import * as constants from "../modules/Constants.js";
import * as THREE from "three";
import DicomPointCloudViz from './DicomPointCloudViz.js';
import DicomSliceViewer from './DicomSliceViewer.js';
import OrganGraphD3 from './OrganGraphD3.js';
import SpatialDoseGlyph from './SpatialDoseGlyph.js'
import Utils from '../modules/Utils.js';
import {Wrap, WrapItem, Center, Spinner, VStack, Box, Button, ButtonGroup,Divider} from '@chakra-ui/react';


function getMaterialArray(renderer){
    const textureLoader = new THREE.TextureLoader();
    var materialArray = [];
    const getMaterial = (s) => {
        let t = textureLoader.load('textures/' + String(s) + '.png');
        if(renderer !== undefined){
            t.anisotropy = renderer.getMaxAnisotropy();
        }
        let material = new THREE.MeshBasicMaterial({map: t});
        materialArray.push(material);
    }
    const files = ['right','left','superior','inferior','anterior','posterior']
    for(let f of files){
        getMaterial(f);
    }
    return materialArray;
}

function pointCloudCenter(pEntry){
    let pClouds = pEntry['point_clouds'];
    let points = [];
    //if I have too many points it crashes so skip these big middle ones
    const skipRois = ['gtv','gtvn','ctv','ptv','tongue','larynx','ipc','spc','mpc'];
    for(let [roi,entry] of Object.entries(pClouds)){
        if(skipRois.indexOf(roi) > -1){continue}
        points.push(...entry['coordinates']);
        //I think this is as high as it goes
        if(points.length > 89000){ break; }
    }
    let centroid = [];
    for(let i of [0,1,2]){
        centroid[i] = Utils.midpoint(points.map(d=>d[i]));
    }
    return centroid
}

export default function DicomViewerContainer(props){

    const pIds = props.selectedCloudIds;
    const pCloudData = props.patientClouds;
    const [pointCloudElements,setPointCloudElements] = useState(<div></div>);

    const canvasRef = useRef(null);
    const raycaster = new THREE.Raycaster();
    const materialArray = getMaterialArray();
    const cameraPositionZ = 500;
    const [renderer, setRenderer] = useState();
    const [mainCamera, setMainCamera] = useState();

    const [brushHeight,setBrushHeight] = useState({'x': 0.0, 'y': 0.0, 'z': 0.0});
    const [brushedOrgan, setBrushedOrgan] = useState('gtv');
    const crossSectionEpsilonXY = 2;
    const crossSectionEpsilonZ = 1;
    const offsetScale = .2;

    function changeBrushHeight(direction){
        let newHeight = brushHeight + (2*crossSectionEpsilonXY*direction);
        setBrushHeight(newHeight);
    }
    

    useEffect(() => {
        if(!canvasRef.current){ return; }
        var h = canvasRef.current.clientHeight*.99;
        var w = canvasRef.current.clientWidth;
        var r = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        r.setClearColor(0x000000, 1);
        r.setPixelRatio(window.devicePixelRatio);
        r.sortObjects = true;
        r.setSize(w,h);
        setRenderer(r);
    },[canvasRef.current]);

    const makeBrushToggleButton = (axis) => {
        const increment = (direction) => {
            let newBrush = Object.assign({},brushHeight);
            newBrush[axis] = newBrush[axis] + (direction);
            setBrushHeight(newBrush)
        };

        return (
            <ButtonGroup isAttached size='sm' gap='0' width='auto' margin='.1em'>
                <Button
                    width='auto'
                    height='100%'
                    colorScheme='teal'
                    onClick={() => increment(1)}
                >{'+'}</Button>
                <Button
                    width='auto'
                    height='100%'
                    colorScheme='teal'
                >
                    {axis + '-offset: ' + (offsetScale*brushHeight[axis]).toFixed(1)}
                </Button>
                <Button
                    width='auto'
                    height='100%'
                    colorScheme='teal'
                    onClick={() => increment(-1)}
                >{'-'}</Button>
            </ButtonGroup>
        )
    }

    useEffect(()=>{
        if(pCloudData === null){
            setPointCloudElements(
                <div className={'fillSpace rounded'} style={{'background':'gray','padding':'15%'}}>
                    <Spinner className={'fillSpace'} size='xl'></Spinner>
                </div>
            );

        }
        else{
            const makeSliceViewer = (d,axis,centroid) => {
                return (
                    <VStack w='15vw' h='12vw' className={'lightGutter shadow'}>
                        <Center w='15vw' h='11vw'>
                            <DicomSliceViewer
                                pCloudData={d}
                                raycaster={raycaster}
                                offset={brushHeight[axis]}
                                setBrushHeight={setBrushHeight}
                                epsilon={axis === 'z'? crossSectionEpsilonZ:crossSectionEpsilonXY}
                                changeBrushHeight={changeBrushHeight}
                                brushedOrgan={brushedOrgan}
                                setBrushedOrgan={setBrushedOrgan}
                                crossSectionAxis={axis}
                                offsetScale={offsetScale}
                                centroid={centroid}
                            ></DicomSliceViewer>
                        </Center>
                        <Divider/>
                        <Center w='15vw'  h='1vw'>
                            {Utils.getVarDisplayName(brushedOrgan) + ' slice (' + axis + ') '}
                            {makeBrushToggleButton(axis)}
                        </Center>
                    </VStack>
                )
            }
            let pCloudEntries = pCloudData.map((d,i)=> {
                const centroid = pointCloudCenter(d);
                return (
                <WrapItem key={'dicomview'+i} className={'shadow'}>
                    <Box>
                        <VStack w='25vw' h ='25vw' className={'lightGutter shadow'}>
                        <Center w='25vw' h='1vw'>
                            {'Patient: ' + d.patient_id}
                        </Center>
                        <Divider></Divider>
                        <Center w='25vw' h='24vw'>
                        <DicomPointCloudViz
                            data={d}
                            renderer={renderer}
                            mainCamera={mainCamera}
                            setMainCamera={setMainCamera}
                            materialArray={materialArray}
                            cameraPositionZ={cameraPositionZ}
                            raycaster={raycaster}
                            brushedOrgan={brushedOrgan}
                            centroid={centroid}
                            setBrushedOrgan={setBrushedOrgan}
                        ></DicomPointCloudViz>
                        </Center>
                        </VStack>
                    </Box>
                    <Box>
                        <VStack w='15vw' h='25vw'>
                        {makeSliceViewer(d,'z',centroid)}
                        {makeSliceViewer(d,'x',centroid)}
                        </VStack>
                    </Box>
                    <Box>
                    <VStack w='15vw' h='25vw'>
                        {makeSliceViewer(d,'y',centroid)}
                        <Center w='15vw' h = '12vw' className={'lightGutter shadow'}>
                            {/* <OrganGraphD3
                                data={d}
                                parameters={props.parameters}
                                brushedOrgan={brushedOrgan}
                                setBrushedOrgan={setBrushedOrgan}
                            /> */}
                            <SpatialDoseGlyph
                                data={d}
                                parameters={props.parameters}
                                brushedOrgan={brushedOrgan}
                                centroid={centroid}
                                setBrushedOrgan={setBrushedOrgan}
                            />
                        </Center>
                        </VStack>
                    </Box>
                </WrapItem>
                )
            });
            setPointCloudElements(
                <Wrap align='center' className={'fillSpace'}>
                    {pCloudEntries}
                </Wrap>
            );
        }
    },[pCloudData,pIds,brushHeight.x,brushHeight.y,brushHeight.z,brushedOrgan,mainCamera])

    return <div style={{'height':'auto','overflowY':'visible','width':'100%'}}
        // onKeyDown={handleKeyPress}
        tabIndex="0"
    >
        {pointCloudElements}
    </div>
}