
import React, {useEffect, useState} from 'react';
// import React from 'react';
import './App.css';

// 1. import `ChakraProvider` component
import { ChakraProvider,Grid,GridItem } from '@chakra-ui/react';

import DataService from './modules/DataService';
import Utils from './modules/Utils';

import DicomViewerContainer from './components/DicomViewerContainer.js';
import ScatterPlotD3 from './components/ScatterPlotsD3.js';

function App() {
  // 2. Wrap ChakraProvider at the root of your app
  var api = new DataService();

  //this gets an object with general bounds of data
  //currently: fields: valid fields with patient data, patientIds: patient Ids we can get, 
  //rois: organ names, roiMap: map of index -> organ name for masks
  const [parameters, setParameters] = useState({});

  const [patientClouds, setPatientClouds] = useState(null);
  const [patientDicoms, setPatientDicoms] = useState(null);

  const [selectedCloudIds, setSelectedCloudIds] = useState([
    1087308891, 
    1108642427,
  ]);

  //as of writting this is {'distances': NxO array of gtv -> organ distanes, 'patients': list of patient ids in the order of the array, roiOrder: list of rois in the order of the array}
  const [patientDistanceData,setPatientDistanceData] =  useState(null);

  const fetchDetails = async () => {
    const params = await api.getDetails();
    console.log('get details',params);
    setParameters(params);
  }

  // const fetchPatientRecords = async(patientIds, fields,setFunction) => {
  //   //meant to fetch a generic set of patient stuff so I can reuse this for different kinds of fields
  //   //set function is a state updator like setPatientData
  //   //sort of outdated now
  //   const pData = await api.getPatientData(patientIds,fields);
  //   // console.log('got patient data',patientIds,fields);
  //   console.log(pData);
  //   setFunction(pData);
  // }

  const fetchPatientClouds = async(patientIds) => {
    setPatientClouds(null);
    const pData = await api.getPatientFiles(patientIds,'pclouds');
    console.log('patient clouds',pData);
    setPatientClouds(pData);
  }

  //for later
  const fetchPatientDicoms = async(patientIds) => {
    setPatientDicoms(null);
    const pData = await api.getPatientFiles(patientIds,'images');
    console.log('patient dicoms',pData);
    setPatientDicoms(pData);
  }

  const fetchDistances = async() => {
    setPatientDistanceData(null);
    const dData = await api.getPatientDistances();
    setPatientDistanceData(dData);
  }

  useEffect(() => {
    // console.log('fetching')
    fetchDetails();
  },[]) 

  useEffect(() => {
    fetchDistances();
  },[])

  useEffect(() => {
    fetchPatientClouds(selectedCloudIds);
  },[selectedCloudIds]);


  return (
    <ChakraProvider>
      <Grid
        h='100%'
        w='100%'
        templateRows='2em repeat(4,1fr)'
        templateColumns='calc(55vw + 1em) repeat(2,1fr)'
        gap={1}
      >
        <GridItem rowSpan={1} colSpan={3} bg='green'>
          {'top'}
        </GridItem>
        <GridItem rowSpan={4} className={'shadow scroll'} colSpan={1}>
          <DicomViewerContainer
            selectedCloudIds={selectedCloudIds}
            patientClouds={patientClouds}
            patientDicoms={patientDicoms}
            parameters={parameters}
            distanceData={patientDistanceData}
          >
          </DicomViewerContainer>
        </GridItem>
        <GridItem rowSpan={2} colSpan={2} className={'shadow'}>
          <ScatterPlotD3
            key={selectedCloudIds[0]}
            distanceData={patientDistanceData}
            parameters={parameters}
            selectedCloudIds={selectedCloudIds}
            setSelectedCloudIds={setSelectedCloudIds}
          />
        </GridItem>
        {/* <GridItem rowSpan={1} colSpan={2} className={'shadow'}>
          {'4'}
        </GridItem> */}
        <GridItem rowSpan={2} colSpan={2} className={'shadow'}>
          {'5'}
        </GridItem>
      </Grid>
    </ChakraProvider>
  )
}

export default App;
