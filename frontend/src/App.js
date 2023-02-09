
import React, {useEffect, useState} from 'react';
// import React from 'react';
import './App.css';

// 1. import `ChakraProvider` component
import { ChakraProvider,Grid,GridItem } from '@chakra-ui/react';

import DataService from './modules/DataService';
import Utils from './modules/Utils';

import DicomViewerContainer from './components/DicomViewerContainer.js';

function App() {
  // 2. Wrap ChakraProvider at the root of your app
  var api = new DataService();

  //this gets an object with general bounds of data
  //currently: fields: valid fields with patient data, patientIds: patient Ids we can get, 
  //rois: organ names, roiMap: map of index -> organ name for masks
  const [parameters, setParameters] = useState({});

  const [patientClouds, setPatientClouds] = useState(null);
  const [patientDicoms, setPatientDicoms] = useState(null);
  const [selectedCloudIds, setSelectedCloudIds] = useState([1,3,5]);

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


  useEffect(() => {
    // console.log('fetching')
    fetchDetails();
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
        templateColumns='repeat(3,1fr)'
        gap={1}
      >
        <GridItem rowSpan={1} colSpan={3} bg='green'>
          {'top'}
        </GridItem>
        <GridItem rowSpan={3} className={'shadow scroll'} colSpan={2}>
          <DicomViewerContainer
            selectedCloudIds={selectedCloudIds}
            patientClouds={patientClouds}
            patientDicoms={patientDicoms}
            parameters={parameters}
          >
          </DicomViewerContainer>
        </GridItem>
        <GridItem rowSpan={2} colSpan={1} className={'shadow'}>
          {'3'}
        </GridItem>
        <GridItem rowSpan={1} colSpan={2} className={'shadow'}>
          {'4'}
        </GridItem>
        <GridItem rowSpan={2} colSpan={1} className={'shadow'}>
          {'5'}
        </GridItem>
      </Grid>
    </ChakraProvider>
  )
}

export default App;
