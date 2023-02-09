import React, {useState, useEffect, useRef} from 'react';
import * as constants from "../modules/Constants.js";
import * as THREE from "three";
import DicomPointCloudViz from './DicomPointCloudViz.js';
import DicomSliceViewer from './DicomSliceViewer.js';
import OrganGraphD3 from './OrganGraphD3.js';
import {Wrap, WrapItem, Center, Spinner, VStack, Box} from '@chakra-ui/react';

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

    const [brushHeight,setBrushHeight] = useState(0);
    const [brushedOrgan, setBrushedOrgan] = useState('GTVp');
    const [crossSectionAxis,setCrossSectionAxis] = useState('z');
    const crossSectionEpsilon = .5;

    function changeBrushHeight(direction){
        let newHeight = brushHeight + (2*crossSectionEpsilon*direction);
        setBrushHeight(newHeight);
    }
    

    function handleKeyPress(event){
        // event.stopPropagation();
        //38 => up arrow, 40 = downarrow, 37 = left, 39 = right
        console.log('keyup', event.key,event.keyCode);
        if(event.key === 'ArrowUp'){
            changeBrushHeight(1);
        } else if(event.key === 'ArrowDown'){
            changeBrushHeight(-1);
        }
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

    useEffect(()=>{
        if(pCloudData === null){
            setPointCloudElements(
                <div className={'fillSpace rounded'} style={{'background':'gray','padding':'15%'}}>
                    <Spinner className={'fillSpace'} size='xl'></Spinner>
                </div>
            );

        }
        else{
            // console.log(brushHeight)
            let pCloudEntries = pCloudData.map((d,i)=> {
                return (
                <WrapItem key={'dicomview'+i} className={'shadow'}>
                    <Box onKeyDown={handleKeyPress}>
                        <Center w='25vw' h='25vw'>
                        <DicomPointCloudViz
                            data={d}
                            renderer={renderer}
                            mainCamera={mainCamera}
                            setMainCamera={setMainCamera}
                            materialArray={materialArray}
                            cameraPositionZ={cameraPositionZ}
                            raycaster={raycaster}
                            brushedOrgan={brushedOrgan}
                            setBrushedOrgan={setBrushedOrgan}
                        ></DicomPointCloudViz>
                        </Center>
                    </Box>
                    <Box onKeyDown={handleKeyPress}>
                        <VStack w='15vw' h='25vw'>
                        <Center w='15vw' h = '12vw'>
                        <DicomSliceViewer
                            pCloudData={d}
                            raycaster={raycaster}
                            brushHeight={brushHeight}
                            setBrushHeight={setBrushHeight}
                            epsilon={crossSectionEpsilon}
                            changeBrushHeight={changeBrushHeight}
                            brushedOrgan={brushedOrgan}
                            setBrushedOrgan={setBrushedOrgan}
                            crossSectionAxis={'z'}
                        ></DicomSliceViewer>
                        </Center>
                        <Center w='15vw' h = '12vw'>
                        <DicomSliceViewer
                            pCloudData={d}
                            raycaster={raycaster}
                            brushHeight={brushHeight}
                            setBrushHeight={setBrushHeight}
                            epsilon={2*crossSectionEpsilon}
                            changeBrushHeight={changeBrushHeight}
                            brushedOrgan={brushedOrgan}
                            setBrushedOrgan={setBrushedOrgan}
                            crossSectionAxis={'x'}
                        ></DicomSliceViewer>
                        </Center>
                        </VStack>
                    </Box>
                    <Box>
                        <Center h='25vw' w='25vw'>
                            <OrganGraphD3
                                data={d}
                                parameters={props.parameters}
                                brushedOrgan={brushedOrgan}
                                setBrushedOrgan={setBrushedOrgan}
                            />
                        </Center>
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
    },[pCloudData,pIds,brushHeight,crossSectionAxis,brushedOrgan,mainCamera])

    return <div style={{'height':'auto','overflowY':'visible','width':'100%'}}
        onKeyDown={handleKeyPress}
        tabIndex="0"
    >
        {pointCloudElements}
    </div>
}