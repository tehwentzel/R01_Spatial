class Const():

    #for troubleshooting, will migrate to own file
    data_dir = "../data/" #private data
    resource_dir = "../resources/" #public data (can be on github)
    
    dicom_dir = data_dir + 'DICOMS/'
    unprocessed_dicoms = dicom_dir + 'R01/'
    dicom_test_dir = data_dir + 'SMART/'
    
    pointcloud_dir = dicom_dir + 'ProcessedPatients/'
    small_dist_json = '../data/r01_distances_small.json'
    full_dist_json = '../data/r01_distances.json'
    
    processed_mdasi = '../data/dicom_mdasi.json'
    
    symptoms = ["pain", "fatigue", "nausea", "sleep", 
                "distress", "sob", "memory", "appetite", 
                "drowsy", "drymouth", "sad", "vomit", "numb", 
                "mucus", "swallow", "choke", "voice", "skin", 
                "constipation", "taste", "mucositis", "teeth", 
                "activity", "mood", "work", "relations", "walking",
                "enjoy"]
   
    organ_list = [
        'hyoid',
        'mandible',
#         'brachial_plex_l','brachial_plex_r',
        'brainstem',
        'oral_cavity',
        'glottis',
        'thyroid',
#         'clavicle_l','clavicle_r',
#             'eye_l','eye_r',
        'cricoid',
        'cricopharyngeal_muscle',
        'esophagus',
        'glnd_submand_l','glnd_submand_r',
        'genioglossus_m',
#         'geniohyoid',
        'glottis',
        'hard_palate','soft_palate',
        'ipc','spc','mpc',
        'parotid_l','parotid_r',
        'larynx',
        'supraglottic_larynx',
        'lips_lower','lips_upper',
        'ant_digastric_l','ant_digastric_r',
        'mastoid_l','mastoid_r',
        'medial_pterygoid_l','medial_pterygoid_r',
        'lateral_pterygoid_l','lateral_pterygoid_r',
#         'mylohyoid_l','mylohyoid_r',
        'buccinator_l','buccinator_r',
        'masseter_l','masseter_r',
        'post_digastric_l','post_digastric_r',
        'sternocleidomastoid_l','sternocleidomastoid_r',
        'mylogeniohyoid',
        'post_scalene_l','post_scalene_r',
        'ant_scalene_l','ant_scalene_r',
#         'pharynx',
        'spinal_cord',
        'tongue',
        'pituitary',
#         'trachea',
    ]

    gtv_names = ['gtv','gtvn','ptv','ctv']
    
    bad_ids =[1265845118,1269213210,2815583275,2989874876,3225956079,4443664553,4509480776,9156619185,9920271364,1344996406,1362035218,1401915784,1406457912,1573361627,1931216474,2002304413,2056532905,2304398819,2394091614,2530084611,2692140912,3045110595,3235750820,3316448321,4017119917,2037015898,2111490509,2749596965,2929571068,1306278550,1337145443,2983776095,3035721150,3045918834,9878102359 ]
    
    organ_associations = {
         'glnd_thyroid_l': 'thyroid',
         'glnd_thyroid_r': 'thyroid',
         'mylogeniohyoid': 'hyoid',
         'spinalcord_cerv': 'spinal_cord',
         'brainstem_05': 'brainstem',
         'fs larynx avoid': 'larynx',
         'fsparotid_l_sub_': 'parotid_l',
         'fsparotid_r_sub_': 'parotid_r',
         'glnd_submand_r_': 'glnd_submand_r',
         'mandible_': 'mandible',
         'spinalcord_05_': 'spinal_cord',
         'spinalcord_': 'spinal_cord',
         'spinalcord_prv5': 'spinal_cord',
         'brainstem_prv5': 'brainstem',
         'fsparotid_r_sub': 'parotid_r',
         'fsrtsubmandsub': 'glnd_submand_r',
         'fsrparotidlow': 'parotid_r',
         'fslparotidlow': 'parotid_l',
         'musc_thyrohyoid': 'hyoid',
         'fssubmandib_l_sub': 'glnd_submand_l',
         'spinalcord_05': 'spinal_cord',
         'fsmandibleav70': 'mandible',
         'fsmandibleav70 2': 'mandible',
         'lt_thyroid_lobe': 'thyroid',
         'pituitary_gland': 'pituitary',
         'fs mandible avoid': 'mandible',
         'parotid_l1': 'parotid_l',
         'parotid_r1': 'parotid_r',
         'resd_parotid_r1_ap': 'parotid_r',
         'resd_parotid_l1_ap': 'parotid_l',
         'resd_oral_cavity_ap': 'oral_cavity',
         'resd_glottis_ap': 'glottis',
         'mandible_en_ap': 'mandible',
         'mandible1': 'mandible',
         'larynxavoid': 'larynx',
         'resd_parotid_r_ap': 'parotid_r',
         'resd_mandible_ap': 'mandible',
         'resd_glnd_submand_l_ap': 'glnd_submand_l',
         'fsparotid_l_sub1': 'parotid_l',
         'fsparotid_r_sub1': 'parotid_r',
         'fsmandiblesub': 'mandible',
         'fslarynxexp5mm': 'larynx',
         'fslarynxhot': 'larynx',
         'i-parotid': 'parotid_l',
         'c-parotid': 'parotid_r',
         'lt parotid push': 'parotid_l',
         'lparotidcool': 'parotid_l',
         'spinalcord_05mm': 'spinal_cord',
         'brainstem_03mm': 'brainstem',
         'push tongue': 'tongue',
         'tongue1': 'tongue',
         'rt lacrimal gland': 'lacrimal_r',
         'lt lacrimal gland': 'lacrimal_l',
         'endolarynx': 'larynx',
         'fs parotid_r_sub': 'parotid_r',
         'spinalcord_prv05': 'spinal_cord',
         'brainstem_prv05': 'brainstem',
         'mandible_1': 'mandible',
         'spinalcord1': 'spinal_cord',
         'mandible avoid': 'mandible',
         'rt parotid sub': 'parotid_r',
         'lt parotid sub': 'parotid_l',
         'prv brainstem 5mm': 'brainstem',
         'ltparotidsub': 'parotid_l',
         'mandibleavoid': 'mandible',
         'oldspinal cord': 'spinal_cord',
         'resd_parotid_l_ap': 'parotid_l',
         'resd_larynx_ap': 'larynx',
         'resd_glnd_submand_r_ap': 'glnd_submand_r',
         'fslarynxavoid': 'larynx',
         'resd_thyroid_ap': 'thyroid',
         'fsrparotidavoid': 'parotid_r',
         'fslparotidavoid': 'parotid_l',
         'posterior larynx': 'larynx',
         'fs mandible avoid 1': 'mandible',
         'fs mandible avoid new plan': 'mandible',
         'parotid_r_copy': 'parotid_r',
         'fsrparotidhot': 'parotid_r',
         'fsrparotidhot2': 'parotid_r',
         'fslarynxep5mm': 'larynx',
         'fslparotidhot': 'parotid_l',
         'fshyoidhot': 'hyoid',
         'spinalcord_en_ap': 'spinal_cord',
         'spinalcord_prv5_en_ap': 'spinal_cord',
         'spinal_cord_prv5': 'spinal_cord',
         'pbrainstem cw': 'brainstem',
         'spinalcord_03': 'spinal_cord',
         'larynx sub': 'larynx',
         'fslarynx avoid': 'larynx',
         'fs l parotid push': 'parotid_l',
         'fsl parotid tail': 'parotid_l',
         'fsr parotid tail': 'parotid_r',
         'fsthyroid push': 'thyroid',
         'fs parotid r push top': 'parotid_r',
         'fs parotid l push bottom': 'parotid_l',
         'fsparotid_l_sub2': 'parotid_r',
         'fs rt parotid push': 'parotid_r',
         'fs mandibleavoid': 'mandible',
         'spinal cord_prv5': 'spinal_cord',
         'r lacrimal gland': 'lacrimal_r',
         'l lacrimal gland': 'lacrimal_l',
         'fsr parotid push': 'parotid_r',
         'fsl parotid push': 'parotid_l',
         'fslarynxavoid2': 'larynx',
         'larynxpush': 'larynx',
         'resd_parotid_l_ap_0_ap': 'parotid_l',
         'rt parotid push': 'parotid_r',
         'fs esophagus avoid': 'esophagus',
         'fslarynxavoid5mm': 'larynx',
         'spinal cord expanded 5mm': 'spinal_cord',
         'rt parotid tail': 'parotid_r',
         'fsrt parotid push': 'parotid_r',
         'parotid_lsub': 'parotid_l',
         'fslarynxpush': 'larynx',
         'z larynx avoid': 'larynx',
         'mandible lingula': 'mandible',
         'z_r submandpush': 'glnd_submand_r',
         'gnld_submand_l': 'glnd_submand_l',
         'brainstem expand': 'brainstem',
         'fsparotid_l_sub_1': 'parotid_l',
         'fsparotid_r_sub_1': 'parotid_r',
         'fs_parotid_r_sub': 'parotid_r',
         'fs_parotid_l_sub': 'parotid_l',
         'fs_larynxpush': 'larynx',
         'fsl smg push': 'glnd_submand_l',
         'fs_submand l opt': 'glnd_submand_l',
         'fs_esophagus opt': 'esophagus',
         'fs_larynx opti': 'larynx',
         'larynx_copy': 'larynx',
         'spinal cord 3mm': 'spinal_cord',
         'fs larynx av': 'larynx',
         'fs rsmg av': 'glnd_submand_r',
         'prvbrainstem_5mm': 'brainstem',
         'larynxgsl': 'larynx',
         'x glottis sub': 'glottis',
         'fsmandible prv': 'mandible',
         'fslarynxexp5mmavoid': 'larynx',
         'fsmandible avoid': 'mandible',
        'fscoolrpar': 'parotid_r',
        'fscoollpar': 'parotid_l',
         'fslsmgavoid': 'glnd_submand_l',
         'ltparotidpush': 'parotid_l',
         'resd_larynx avoid_ap_0_ap': 'larynx',
         'resd_esophagus_ap_0_ap': 'esophagus',
         'resd_glnd_submand_r_ap_0_ap': 'glnd_submand_r',
         'fsbrainstem_prv5': 'brainstem',
         'fsspinalcord_prv5': 'spinal_cord',
         'bpr_belowcricoid': 'cricoid',
        't_oral cav avoid': 'oral_cavity',
         'bpl_belowcricoid': 'cricoid',
         'fsrtsmg_sub': 'glnd_submand_r',
        'push esoph post': 'esophagus',
         'fshotmandible': 'mandible',
         'prv brainstem exp 5mm': 'brainstem',
         'fslarynxexp3mm': 'larynx',
         'resd_fslarynxexp3mm_ap': 'larynx',
         'zl submand push': 'glnd_submand_l',
         'resd_esophagus_ap': 'esophagus',
         'partial esophagus': 'esophagus',
         'fs r parotid eud': 'parotid_r',
         'fslt smg push': 'glnd_submand_l',
         'fs_larynx sub': 'larynx',
         'parotid_r_sub': 'parotid_r',
         'thyroid1': 'thyroid',
         'brainstem_5mm': 'brainstem',
         'fsrparotidhi': 'parotid_r',
         'fslparotidhi': 'parotid_l',
         'push r parotid': 'parotid_r',
         'brainstem_old': 'brainstem',
         'spinalcord_old': 'spinal_cord',
         'parotid_r_old': 'parotid_r',
         'parotid_l_old': 'parotid_l',
         'fslarynx5mmavoid': 'larynx',
         'fsltparotidhot': 'parotid_l',
         'larynx exp': 'larynx',
         'rtparotidsub': 'parotid_r',
         'brainstem_prv 5mm': 'brainstem',
        'oral cavity': 'oral_cavity',
         'spinal cord_prv 5mm': 'spinal_cord',
         'fsparotid_r_sub high': 'parotid_r',
         'rtparotid sub low dose': 'parotid_r',
         'parotid_r partial': 'parotid_r',
         'fs spinal cord avoid': 'spinal_cord',
         'lt_ parotid tail': 'parotid_l',
         'fsrtparotidavoid': 'parotid_r',
         'parotid r sub': 'parotid_r',
         'parotid l  sub': 'parotid_l',
         'resd_fsparotid_l_sub_ap_2_ap': 'parotid_l',
         'resd_larynx_ap_2_ap': 'larynx',
         'resd_esophagus_ap_2_ap': 'esophagus',
         'spinalcord_prv5_en_ap_2_ap': 'spinal_cord',
         'brainstem_prv5_en_ap_2_ap': 'brainstem',
         'fslarynx_avoid': 'larynx',
         'fs_glottis avoid': 'glottis',
         'resd_rt parotid_ap': 'parotid_r',
         'resd_l parotid_ap': 'parotid_l',
         'prv brainstem 5mm_en_ap': 'brainstem',
         'z larynx 1cm': 'larynx',
         'z l parotid 1cm': 'parotid_l',
         'parotid_l_1': 'parotid_l',
         'parotid_r_1': 'parotid_r',
         'spinalcord_1': 'spinal_cord',
         'hot mandible': 'mandible',
         'more larynx avoid': 'larynx',
         'rt_parotid tail': 'parotid_r',
         '10gy_larynx': 'larynx',
         'cool_mandible': 'mandible',
         'bone_hyoid': 'hyoid',
         'hyoid_bone': 'hyoid',
         'brachial plex_l': 'brachial_plex_l',
         'brachial plex_r': 'brachial_plex_r',
         'brachialplex_l': 'brachial_plex_l',
         'bracialplex_l_': 'brachial_plex_l',
         'brachialplex_r': 'brachial_plex_r',
         'brachialplex_r_': 'brachial_plex_r',
         'brac_plx_r': 'brachial_plex_r',
         'brac_plx_l': 'brachial_plex_l',
        'fs avcavity_oral': 'oral_cavity',
        'fscavity_oralavd': 'oral_cavity',
         'l brach _3mm': 'brachial_plex_l',
         'r brach _3mm': 'brachial_plex_r',
         'l brachial plexus +2mm': 'brachial_plex_l',
         'r brachial plexus +2mm': 'brachial_plex_r',
         'left b plex': 'brachial_plex_l',
         'right b plex': 'brahcial_plex_r',
         'lt_brachial_plexsus': 'brachial_plex_l',
         'rt_brachial_plexsus': 'brahcial_plex_r',
         'lt_brachial_plexus': 'brachial_plex_l',
         'rt_brachial_plexus': 'brahcial_plex_r',
         'brain stem': 'brainstem',
         'brain stem_en_ap': 'brainstem',
         'brainstem expanded': 'brainstem',
         'brainstem expanded 5mm': 'brainstem',
         'brainstem1': 'brainstem',
         'brainstem2': 'brainstem',
         'brainstem3': 'brainstem',
         'brainstem_': 'brainstem',
         'brainstem_1': 'brainstem',
         'brainstem_03': 'brainstem',
         'expanded brainstem': 'brainstem',
         'bone_mastoid_r': 'mastoid_r',
         'bone_mastoid_l': 'mastoid_l',
         'cavity_oral avoid': 'oral_cavity',
         'cavity_oral': 'oral_cavity',
         'cavity oral': 'oral_cavity',
         'cavity_oral1': 'oral_cavity',
         'cavity_oral_avoid': 'oral_cavity',
         'cavity_oral_avoi': 'oral_cavity',
         'cavity_oral_copy': 'oral_cavity',
         'fs cavity_oral': 'oral_cavity',
         'cavity_oralnorm': 'oral_cavity',
         'extended_oral_cavity': 'oral_cavity',
         'thryoid_lobe': 'thyroid',
         'thyroid_lobe': 'thyroid',
         'thyroid_cartilage': 'thyroid',
         'cartlg_thyroid': 'thyroid',
         'rt_lateral_pterygoid_m': 'lateral_pterygoid_r',
         'lt_lateral_pterygoid_m': 'lateral_pterygoid_l',
         'pterygoid_lat_l': 'lateral_pterygoid_l',
         'pterygoid_lat_r': 'lateral_pterygoid_r',
         'larynx_sg': 'supraglottic_larynx',
         'cricoid_cartilage': 'crocoid',
         'cricopharyngeus': 'cricopharyngeal_muscle',
         'cricopharyngeus muscle': 'cricopharyngeal_muscle',
         'eso': 'esophagus',
         'esophagus avoid': 'esophagus',
         'esophagus1': 'esophagus',
         'esophagus_': 'esophagus',
         'esophagus_u': 'esophagus',
         'esophagus_up': 'esophagus',
         'eye_l_1': 'eye_l',
         'eye_r_1': 'eye_r',
         'fs glnd_submand_l': 'glnd_submand_l',
         'fs glnd_submand_r': 'glnd_submand_r',
         'glnd_submand_l avd': 'glnd_submand_l',
         'glnd_submand_l1': 'glnd_submand_l',
         'glnd_submand_r avd': 'glnd_submand_r',
         'glnd_submand_r1': 'glnd_submand_r',
         'l smg': 'glnd_submand_l',
         'r smg': 'glnd_submand_r',
         'l submandibular gland': 'glnd_submand_l',
         'r submandibular gland': 'glnd_submand_r',
         'l_submand_sub': 'glnd_submand_l',
         'r_submand_sub': 'glnd_submand_r',
         'lt submandib': 'glnd_submand_l',
         'rt submandib': 'glnd_submand_r',
         'lt submandibular': 'glnd_submand_l',
         'rt submandibular': 'glnd_submand_r',
         'lt submandibular gland': 'glnd_submand_l',
         'rt submandibular gland': 'glnd_submand_r',
         'lt_submandibular_gland': 'glnd_submand_l',
         'rt_submandibular_gland': 'glnd_submand_r',
         'left submandibular gland': 'glnd_submand_l',
         'right submandibular gland': 'glnd_submand_r',
         'genioglossus': 'genioglossus_m',
         'glottic_area': 'glottis',
         'glottis_1': 'glottis',
         'hardpalate': 'hard_palate',
         'inferior constrictor': 'ipc',
         'inferior pharyngeal constrictor': 'ipc',
         'l par sub': 'parotid_l',
         'l parotid': 'parotid_l',
         'r par sub': 'parotid_r',
         'r parotid': 'parotid_r',
         'l parotids': 'parotid_l',
         'r parotids': 'parotid_r',
         'parotid_left': 'parotid_l',
         'parotid_right': 'parotid_r',
         'left parotid': 'parotid_l',
         'right parotid': 'parotid_r',
         'lt parotid': 'parotid_l',
         'rt parotid': 'parotid_r',
         'lt_parotid_gland': 'parotid_l',
         'rt_parotid_gland': 'parotid_r',
         'lparotid': 'parotid_l',
         'rparotid': 'parotid_r',
         'fsparotid_l_sub': 'parotid_l',
         'fspartoid_r_sub': 'parotid_r',
         'fs parotid_l_sub': 'parotid_l',
         'fs partoid_r_sub': 'parotid_r',
         'larynx avoid': 'larynx',
         'larynx and pharynx wall': 'larynx',
         'larynx avoidance': 'larynx',
         'larynx normal': 'larynx',
         'larynx proper': 'larynx',
         'larynx1': 'larynx',
         'larynx_': 'larynx',
         'larynx_avd': 'larynx',
         'larynx_avoid': 'larynx',
         'larynxnormal': 'larynx',
         'largnx_sg': 'supraglottic_larynx',
         'larynx_above iso': 'supraglottic_larynx',
         'lower_lip': 'lips_lower',
         'upper_lip': 'lips_upper',
         'lt ant digastric': 'ant_digastric_l',
         'rt ant digastric': 'ant_digastric_r',
         'lt_ant_digastric_m': 'ant_digastric_l',
         'rt_ant_digastric_m': 'ant_digastric_r',
         'lt mastoid': 'mastoid_l',
         'rt mastoid': 'mastoid_r',
         'lt_mastoid': 'mastoid_l',
         'rt_mastoid': 'mastoid_r',
         'lt medial ptrygoid(2)': 'medial_pterygoid_l',
         'rt medial ptrygoid(2)': 'medial_pterygoid_r',
         'lt_medial_pterygoid_m': 'medial_pterygoid_l',
         'rt_medial_pterygoid_m': 'medial_pterygoid_r',
         'pterygoid_med_l': 'medial_pterygoid_l',
         'pterygoid_med_r': 'medial_pterygoid_l',
         'lt myelohyoid': 'mylohyoid_l',
         'rt myelohyoid': 'mylohyoid_r',
         'lt_buccinator_m': 'buccinator_l',
         'rt_buccinator_m': 'buccinator_r',
         'lt_masseter_m': 'masseter_l',
         'rt_masseter_m': 'masseter_r',
         'lt_post_digastric_m': 'post_digastric_l',
         'rt_post_digastric_m': 'post_digastric_r',
         'lt_sternocleidomastoid_m': 'sternocleidomastoid_l',
         'rt_sternocleidomastoid_m': 'sternocleidomastoid_r',
         'i-smg': 'glnd_submand_l',
         'c-smg': 'glnd_submand_r',
         'lt_thryoid_lobe': 'thyroid',
         'rt_thyroid_lobe': 'thyroid',
         'bone_mandible': 'mandible',
         'musc_buccinat_l': 'buccinator_l',
         'musc_buccinat_r': 'buccinator_r',
         'musc_geniogloss': 'genioglossus_m',
         'musc_digastric_la': 'ant_digastric_l',
         'musc_digastric_lp': 'post_digastric_l',
         'musc_digastric_ra': 'ant_digastric_r',
         'musc_digastric_rp': 'post_digastric_r',
         'musc_masseter_l': 'masseter_l',
         'musc_masseter_r': 'masseter_r',
         'musc_mghcomplex': 'mylogeniohyoid',
         'musc_sclmast_l': 'sternocleidomastoid_l',
         'musc_sclmast_r': 'sternocleidomastoid_r',
         'mylogeniohyoid_m': 'mylogeniohyoid',
         'mylohyoid_m': 'mylogeniohyoid',
         'oralcavity': 'oral_cavity',
         'palate_soft': 'soft_palate',
         'softpalate': 'soft_palate',
         'soft palate': 'soft_palate',
         'soft_palate1': 'soft_palate',
         'smg_l': 'glnd_submand_l',
         'smg_r': 'glnd_submand_r',
         'spinal cord': 'spinal_cord',
         'spinalcord': 'spinal_cord',
         'submandibula_l': 'glnd_submand_l',
         'submandibula_r': 'glnd_submand_r',
         'submandibular_l': 'glnd_submand_l',
         'submandibular_r': 'glnd_submand_r',
         'submnd_salv_l': 'glnd_submand_l',
         'submnd_salv_r': 'glnd_submand_r',
         'submand_salv_l1': 'glnd_submand_l',
         'submand_salv_r1': 'glnd_submand_r',
         'superior constrictor': 'spc',
         'superior constrictor muscle': 'spc',
         't esophagus': 'esophagus',
         't larynx': 'larynx',
         'x larynx 1cm': 'larynx',
         'tongue_base': 'tongue',
         'x r parotid 1cm': 'parotid_r',
         'x l parotid 1cm': 'parotid_l',
         'musc_constrict_m': 'mpc',
         'musc_constrict_s': 'spc',
         'musc_constrict_i': 'ipc',
        'cornea_l': 'eye_l',
        'cornea_r': 'eye_r',
        'lt_anterior_seg_eyeball':'eye_l',
        'rt_anterior_seg_eyeball' :'eye_r',
        'lens_l': 'eye_l',
        'lens_r': 'eye_r',
        'musc_scalene_lp': 'post_scalene_l',
        'musc_scalene_rp': 'post_scalene_r',
        'musc_scalene_la': 'ant_scalene_l',
        'musc_scalene_r': 'ant_scalene_r',
        'posterior larynx': 'larynx',
        'fslpaortidlow': 'parotid_l',
        'fsrpaortidlow': 'parotid_r',
        'brachialplex_l1': 'brachial_plex_l',
        'brachialplex_r1': 'brachial_plex_r',
        'brachialplex_l_1': 'brachial_plex_l',
        'brachialplex_l_1': 'brachial_plex_r',
        'fscavity_oral': 'oral_cavity',
        'fs avoid mandibl': 'mandible',
        'fscavity_oral avoid': 'oral_cavity',
        'resd_cavity_oral_ap': 'oral_cavity',
        'resd_fs cavity_oral avoid_ap': 'oral_cavity',
        't sumandibular r': 'glnd_submand_r',
        't sumandibular l': 'gnld_submand_l',
        'rt_anterior_scalene_m': 'ant_scalene_r',
        'lt_anterior_scalene_m': 'ant_scalene_l',
        'lt_posterior_scalenes_m': 'post_scalene_l',
        'rt_posterior_scalenes_m': 'post_scalene_r',
        'musc_scalene_ra': 'ant_scalene_r',
        'musc_scalene_la': 'ant_scalene_l',
        'lt_posterior_seg_eyeball': 'eye_l',
        'rt_posterior_seg_eyeball': 'eye_r',
        }
    
#     organ_associations = {
#     'bone_hyoid': 'hyoid',
#     'hyoid_bone': 'hyoid',
#         'cornea_l': 'eye_l',
#         'cornea_r': 'eye_r',
#         'lt_anterior_seg_eyeball':'eye_l',
#         'rt_anterior_seg_eyeball' :'eye_r',
#         'lens_l': 'eye_l',
#         'lens_r': 'eye_r',
#         'musc_scalene_lp': 'post_scalene_l',
#         'musc_scalene_rp': 'post_scalene_r',
#         'musc_scalene_la': 'ant_scalene_l',
#         'musc_scalene_r': 'ant_scalene_r',
#         'posterior larynx': 'larynx',
#     'brachial plex_l': 'brachial_plex_l',
#     'brachial plex_r': 'brachial_plex_r',
#     'brachialplex_l': 'brachial_plex_l',
#     'bracialplex_l_': 'brachial_plex_l',
#     'brachialplex_r': 'brachial_plex_r',
#     'brachialplex_r_': 'brachial_plex_r',
#     'l brach _3mm': 'brachial_plex_l',
#     'r brach _3mm': 'brachial_plex_r',
#     'l brachial plexus +2mm': 'brachial_plex_l',
#     'r brachial plexus +2mm': 'brachial_plex_r',
#     'left b plex': 'brachial_plex_l',
#     'right b plex': 'brahcial_plex_r',
#     'lt_brachial_plexsus': 'brachial_plex_l',
#     'rt_brachial_plexsus': 'brahcial_plex_r',
#       'lt_brachial_plexus': 'brachial_plex_l',
#     'rt_brachial_plexus': 'brahcial_plex_r',
#     'brain stem': 'brainstem',
#     'brain stem_en_ap': 'brainstem',
#     'brainstem expanded': "brainstem",
#     'brainstem expanded 5mm': "brainstem",
#     'brainstem1': "brainstem",
#     'brainstem2': "brainstem",
#     'brainstem3': "brainstem",
#     'brainstem_': "brainstem",
#     'brainstem_1': "brainstem",
#     'brainstem_03': "brainstem",
#     'brainstem_1': "brainstem",
#     'expanded brainstem': 'brainstem',
#         'bone_mastoid_r': 'mastoid_r',
#         'bone_mastoid_l': 'mastoid_l',
#     'cavity_oral avoid': 'oral_cavity',
#     'cavity_oral': 'oral_cavity',
#     'cavity_oral1': 'oral_cavity',
#     'cavity_oral_avoid': 'oral_cavity',
#     'cavity_oral_avoi': 'oral_cavity',
#     'cavity_oral_copy': 'oral_cavity',
#     'fs cavity_oral': 'oral_cavity',
#     'cavity_oralnorm': 'oral_cavity',
#     'extended_oral_cavity': 'oral_cavity',
#     'thryoid_lobe': 'thyroid',
#         'thyroid_lobe': 'thyroid',
#         'thyroid_cartilage': 'thyroid',
#         'cartlg_thyroid': 'thyroid',
#      'rt_lateral_pterygoid_m': 'lateral_pterygoid_r',
#         'lt_lateral_pterygoid_m': 'lateral_pterygoid_l',
#    'pterygoid_lat_l': 'lateral_pterygoid_l',
#         'pterygoid_lat_r': 'lateral_pterygoid_r',
#     'larynx_sg': 'supraglottic_larynx',
#     'cricoid_cartilage': 'crocoid',
#     'cricopharyngeus': 'cricopharyngeal_muscle',
#     'cricopharyngeus muscle': 'cricopharyngeal_muscle',
#     'eso': 'esophagus',
#     'esophagus avoid': 'esophagus',
#     'esophagus1': 'esophagus',
#     'esophagus_':'esophagus',
#     'esophagus_u': 'esophagus',
#     'esophagus_up': 'esophagus',
#     'eye_l_1':'eye_l',
#     'eye_r_1':'eye_r',
#     'fs glnd_submand_l': 'glnd_submand_l',
#     'fs glnd_submand_r': 'glnd_submand_r',

#     'glnd_submand_l avd': 'glnd_submand_l',
#     'glnd_submand_l1': 'glnd_submand_l',
#     'glnd_submand_r avd': 'glnd_submand_r',
#     'glnd_submand_r1': 'glnd_submand_r',
#     'l smg': 'glnd_submand_l',
#     'r smg': 'glnd_submand_r',
#     'l submandibular gland': 'glnd_submand_l',
#     'r submandibular gland': 'glnd_submand_r',
#     'l_submand_sub': 'glnd_submand_l',
#     'r_submand_sub': 'glnd_submand_r',
#     'lt submandib': 'glnd_submand_l',
#     'rt submandib': 'glnd_submand_r',
#     'lt submandibular': 'glnd_submand_l',
#     'rt submandibular': 'glnd_submand_r',
#     'lt submandibular gland': 'glnd_submand_l',
#     'rt submandibular gland': 'glnd_submand_r',
#     'lt_submandibular_gland': 'glnd_submand_l',
#     'rt_submandibular_gland': 'glnd_submand_r',
#     'left submandibular gland': 'glnd_submand_l',
#     'right submandibular gland': 'glnd_submand_r',
#     'genioglossus':'genioglossus_m',
#     'glottic_area': 'glottis',
#     'glottis_1':'glottis',
#     'hardpalate': 'hard_palate',
#     'inferior constrictor': 'ipc',
#     'inferior pharyngeal constrictor': 'ipc',
#     'l par sub': 'parotid_l',
#     'l parotid': 'parotid_l',
#     'r par sub': 'parotid_r',
#     'r parotid': 'parotid_r',
#     'l parotids': 'parotid_l',
#     'r parotids': 'parotid_r',
#     'parotid_left': 'parotid_l',
#     'parotid_right': 'parotid_r',
#     'left parotid': 'parotid_l',
#     'right parotid': 'parotid_r',
#     'lt parotid': 'parotid_l',
#     'rt parotid': 'parotid_r',
#     'lt_parotid_gland': 'parotid_l',
#     'rt_parotid_gland': 'parotid_r',
#     'lparotid': 'parotid_l',
#     'rparotid': 'parotid_r',
#      'fsparotid_l_sub': 'parotid_l',
#      'fspartoid_r_sub': 'parotid_r',
#      'fs parotid_l_sub': 'parotid_l',
#      'fs partoid_r_sub': 'parotid_r',
#     'larynx avoid': 'larynx',
#     'larynx and pharynx wall': 'larynx',
#     'larynx avoidance': 'larynx',
#     'larynx normal': 'larynx',
#     'larynx proper': 'larynx',
#     'larynx1': 'larynx',
#     'larynx_': 'larynx',
#     'larynx_avd': 'larynx',
#     'larynx_avoid': 'larynx',
#     'larynxnormal': 'larynx',
#     'largnx_sg': 'supraglottic_larynx',
#     'larynx_above iso':'supraglottic_larynx',
#     'lower_lip': 'lips_lower',
#     'upper_lip': 'lips_upper',
#     'lt ant digastric': 'ant_digastric_l',
#     'rt ant digastric': 'ant_digastric_r',
#     'lt_ant_digastric_m': 'ant_digastric_l',
#     'rt_ant_digastric_m': 'ant_digastric_r',
#     'lt mastoid': 'mastoid_l',
#     'rt mastoid': 'mastoid_r',
#     'lt_mastoid':'mastoid_l',
#     'rt_mastoid': 'mastoid_r',
#     'lt medial ptrygoid(2)': 'medial_pterygoid_l',
#     'rt medial ptrygoid(2)': 'medial_pterygoid_r',
#     'lt_medial_pterygoid_m':'medial_pterygoid_l',
#     'rt_medial_pterygoid_m':'medial_pterygoid_r',
#     'pterygoid_med_l': 'medial_pterygoid_l',
#      'pterygoid_med_r': 'medial_pterygoid_l',
#     'lt myelohyoid': 'mylohyoid_l',
#     'rt myelohyoid': 'mylohyoid_r',
#     'lt_buccinator_m': 'buccinator_l',
#     'rt_buccinator_m': 'buccinator_r',
#     'lt_masseter_m':'masseter_l',
#     'rt_masseter_m':'masseter_r',
#     'lt_post_digastric_m':'post_digastric_l',
#     'rt_post_digastric_m':'post_digastric_r',
#     'lt_sternocleidomastoid_m': 'sternocleidomastoid_l',
#     'lt_sternocleidomastoid_m':'sternocleidomastoid_l',
#     'rt_sternocleidomastoid_m':'sternocleidomastoid_r',
#     'i-smg': 'sternocleidomastoid_l',
#         'c-smg': 'sternocleidomastoid_l',
#     'lt_thryoid_lobe':'thyroid',
#     'rt_thyroid_lobe': 'thyroid',#im just merging all thyroid stuff
#     'bone_mandible': 'mandible',
#     'musc_buccinat_l':'buccinator_l',
#     'musc_buccinat_r':'buccinator_r',
#     'musc_geniogloss':'genioglossus_m',
#     'musc_digastric_la': 'ant_digastric_l',
#     'musc_digastric_lp': 'post_digastric_l',
#     'musc_digastric_ra': 'ant_digastric_r',
#     'musc_digastric_rp': 'post_digastric_r',
#     'musc_masseter_l': 'masseter_l',
#     'musc_masseter_r':'masseter_r',
#     'musc_mghcomplex': 'mylogeniohyoid',
#     'musc_sclmast_l':'sternocleidomastoid_l',
#     'musc_sclmast_r': 'sternocleidomastoid_r',
#     'mylogeniohyoid_m': 'mylogeniohyoid',
#     'mylohyoid_m': 'mylogeniohyoid',
#     'oralcavity': 'oral_cavity',
#     'palate_soft': 'soft_palate',
#     'softpalate': 'soft_palate',
#     'soft palate': 'soft_palate',
#     'soft_palate1': 'soft_palate',
#     'smg_l': 'glnd_submand_l',
#     'smg_r':'glnd_submand_r',
#     'spinal cord': 'spinal_cord',
#     'spinalcord': 'spinal_cord',
#     'submandibula_l':'glnd_submand_l',
#     'submandibula_r':'glnd_submand_r',
#     'submandibular_l':'glnd_submand_l',
#     'submandibular_r':'glnd_submand_r',
#     'submnd_salv_l': 'glnd_submand_l',
#     'submnd_salv_r': 'glnd_submand_r',
#     'submand_salv_l1': 'glnd_submand_l',
#     'submand_salv_r1':'glnd_sumband_r',
#     'superior constrictor': 'spc',
#     'superior constrictor muscle': 'spc',
#     't esophagus': 'esophagus',
#     't larynx': 'larynx',
#     'x larynx 1cm': 'larynx',
#     'tongue_base': 'tongue',
#         'x r parotid 1cm': 'parotid_r',
#         'x l parotid 1cm': 'parotid_l',
#         'musc_constrict_m': 'mpc',
#         'musc_constrict_s': 'spc',
#         'musc_constrict_i': 'ipc',
#     'glnd_thyroid_l': 'thyroid',
#         'glnd_thryoid_r': 'thyroid',
#         'fs larynx avoid': 'larynx',
#         'fsparotid_l_sub_': 'parotid_l',
#         'fsparotid_r_sub_': 'parotid_r',
#         'fsparotid_l_sub': 'parotid_l',
#         'fsparotid_r_sub': 'parotid_r',
#         'mandible_': 'mandible',
#         'glnd_submand_r_': 'glnd_submand_r',
#         'glnd_submand_l_': 'glnd_submand_l',
#         'spinalcord_': 'spinal_cord',
#         'spinalcord_cerv': 'spinal_cord',
#         'brainstem_prv5': 'brainstem',
#         'fsmandibleav70 2': 'mandible',
#         'fsmandibleav70': 'mandible',
#         'spinalcord_05': 'spinal_cord',
#         'pituitary_gland': 'pituitary',
#         'lt_thyroid_lobe': 'thyroid',
#         'rt_thryoid_lobe': 'thryoid',
#         'fs mandible avoid': 'mandible',
#         'parotid_r1': 'parotid_r',
#         'parotid_l1': 'parotid_l',
#         'resd_parotid_r1_ap': 'parotid_r',
#         'resd_parotid_l1_ap': 'parotid_l',
#         'submnd_salv_r1': 'glnd_submand_r',
#         'submnd_salv_l1': 'glnd_submand_l',
#         'resd_glnd_submand_l_ap': 'glnd_submand_l',
#         'resd_glnd_submand_r_ap': 'glnd_submand_r',
#         'pbrainstem cw': 'brainstem',
#         'parotid_lsub': 'parotid_l',
#         'parotid_rsub': 'parotid_r',
#         'prv brainstem 5mm_en_ap': 'brainstem'
#         'fs_glottis avoid': 'glottis',
#         'fs parotid_r_sub': 'parotid_r',
#         'fs parotid_l_sub': 'parotid_l',
#         'fsparotid_r_sub high': 'parotid_r',
#         'fsparotid_l_sub high': 'parotid_l',
#         'resd_esophagus_ap_0_ap': 'esophagus',
#         'fslarynx_avoid': 'larynx',
#         'resd_fslarynxexp3mm_ap': 'larynx', 
# }
