import axios from 'axios';
import * as constants from './Constants';
const querystring = require('querystring-es3');

export default class DataService {

    constructor(args){
        this.api = axios.create({
            baseURL: constants.API_URL,
        })
    }

    getParamList(pObj){
        let newParams = {}
        let empty= true;
        for(let k of Object.keys(pObj)){
            if(pObj[k] !== undefined & pObj[k] !== null){
                newParams[k] = pObj[k];
                empty = false;
            }
        }
        let paramQuery = '';
        if(!empty){
            let pstring = querystring.stringify(newParams);
            paramQuery = paramQuery + '?' + pstring
        }
        return paramQuery
    }

    async getPatientData(patientIds,fields){
        try{
            var params = {
                'patientIds': patientIds,
                'patientFields': fields,
            }
            let qstring = '/patientdata';
            qstring += this.getParamList(params);
            const response = await this.api.get(qstring);
            return response.data;
        } catch(error){
            console.log('error in getPatientData');
            console.log(error);
        }
        
    }

    async getMdasiData(){
        try{
            const response = await this.api.get('/mdasi')
            return response.data
        } catch(error){
            console.log('error in getMdasiData:')
            console.log(error)
        }
    }

    async getPatientDistances(patientIds){
        //will evantually make this a single file
        try{
            const response = await this.api.get('/distances')
            return response.data
        } catch(error){
            console.log('error in getpatientclouds:');
            console.log(error)
        }
    }

    async getPatientFiles(patientIds,root){
        //root = pclouds for patient clouds, images for patient images
        if(root == undefined){
            root = 'pclouds'
        }
        try{
            var params = {
                'patientIds': patientIds
            }
            let qstring = '/' + root + this.getParamList(params);
            const response = await this.api.get(qstring);
            return response.data;
        } catch(error){
            console.log('error in getpatientclouds');
            console.log(error)
        }
    }

    async getDetails(){
        console.log('called get details')
        try{
            const response = await this.api.get('/parameters');
            console.log('details',response.data);
            return response.data;
        } catch(error){
            console.log(error);
        }

    }




}