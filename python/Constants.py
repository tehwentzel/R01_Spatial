class Const():

    #for troubleshooting, will migrate to own file
    data_dir = "../data/" #private data
    resource_dir = "../resources/" #public data (can be on github)
    
    dicom_dir = data_dir + '/DICOM/'
    dicom_test_dir = data_dir + '/SMART/'
    pointcloud_dir = data_dir + 'PatientPointClouds/'
    
    old_organ_list = [
        'Esophagus',#
         'Spinal_Cord',#
         'Lt_Brachial_Plexus',
         'Rt_Brachial_Plexus',
         'Cricopharyngeal_Muscle',#
#          'Lt_thyroid_lobe',
#          'Rt_thyroid_lobe',
         'Cricoid_cartilage',#
         'IPC',#
         'MPC',#
         'Brainstem',#
         'Larynx',#
         'Thyroid_cartilage',#
         'Rt_Sternocleidomastoid_M',
         'Rt_Mastoid',
         'Rt_Parotid_Gland',
         'Rt_Medial_Pterygoid_M',
         'Rt_Lateral_Pterygoid_M',
         'Rt_Masseter_M',
         'Lt_Sternocleidomastoid_M',
         'Lt_Mastoid',
         'Lt_Parotid_Gland',
         'Lt_Submandibular_Gland',
         'Lt_Medial_Pterygoid_M',
         'Lt_Lateral_Pterygoid_M',
         'Lt_Masseter_M',
         'Supraglottic_Larynx',#
         'SPC',#
         'Rt_Submandibular_Gland',
         'Hyoid_bone',#
         'Soft_Palate',#
         'Genioglossus_M',#
         'Tongue',#
         'Rt_Ant_Digastric_M',
         'Lt_Ant_Digastric_M',
         'Mylogeniohyoid_M',#
         'Extended_Oral_Cavity',#
         'Mandible',#
         'Hard_Palate',
#          'Lt_Posterior_Seg_Eyeball',
#          'Rt_Posterior_Seg_Eyeball',
#          'Lt_Anterior_Seg_Eyeball',
#          'Rt_Anterior_Seg_Eyeball',
         'Lower_Lip',
         'Upper_Lip',
         'Glottic_Area',
                 ]
    
    organ_list = [
        'hyoid',
        'mandible',
        'brachial_plex_l','brachial_plex_r',
        'brainstem',
        'oral_cavity',
        'glottis',
        'thyroid',
#         'clavicle_l','clavicle_r',
#         'cornea_l','cornea_r',
#             'lens_l','lens_r',
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
#         'mylogeniohyoid',
#         'pharynx',
        'spinal_cord',
        'tongue',
        'pituitary',
#         'trachea',
    ]

    gtv_names = ['gtv','gtvn','ptv','ctv']
    organ_associations = {
    'bone_hyoid': 'hyoid',
    'hyoid_bone': 'hyoid',
    'brachial plex_l': 'brachial_plex_l',
    'brachial plex_r': 'brachial_plex_r',
    'brachialplex_l': 'brachial_plex_l',
    'bracialplex_l_': 'brachial_plex_l',
    'brachialplex_r': 'brachial_plex_r',
    'brachialplex_r_': 'brachial_plex_r',
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
    'brainstem expanded': "brainstem",
    'brainstem expanded 5mm': "brainstem",
    'brainstem1': "brainstem",
    'brainstem2': "brainstem",
    'brainstem3': "brainstem",
    'brainstem_': "brainstem",
    'brainstem_1': "brainstem",
    'brainstem_03': "brainstem",
    'brainstem_1': "brainstem",
    'expanded brainstem': 'brainstem',
        'bone_mastoid_r': 'mastoid_r',
        'bone_mastoid_l': 'mastoid_l',
    'cavity_oral avoid': 'oral_cavity',
    'cavity_oral': 'oral_cavity',
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
    'esophagus_':'esophagus',
    'esophagus_u': 'esophagus',
    'esophagus_up': 'esophagus',
    'eye_l_1':'eye_l',
    'eye_r_1':'eye_r',
    'fs glnd_submand_l': 'glnd_submand_l',
    'fs glnd_submand_r': 'glnd_submand_r',

    'glnd_submand_l avd': 'glnd_submand_l',
    'glnd_submand_l1': 'glnd_submand_l',
    'glnd_submand_r avd': 'glnd_submand_r',
    'glnd_submand_r1': 'glnd_submand_r',
    'l smg': 'gnld_submand_l',
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
    'genioglossus':'genioglossus_m',
    'glottic_area': 'glottis',
    'glottis_1':'glottis',
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
    'larynx_above iso':'supraglottic_larynx',
    'lower_lip': 'lips_lower',
    'upper_lip': 'lips_upper',
    'lt ant digastric': 'ant_digastric_l',
    'rt ant digastric': 'ant_digastric_r',
    'lt_ant_digastric_m': 'ant_digastric_l',
    'rt_ant_digastric_m': 'ant_digastric_r',
    'lt mastoid': 'mastoid_l',
    'rt mastoid': 'mastoid_r',
    'lt_mastoid':'mastoid_l',
    'rt_mastoid': 'mastoid_r',
    'lt medial ptrygoid(2)': 'medial_pterygoid_l',
    'rt medial ptrygoid(2)': 'medial_pterygoid_r',
    'lt_medial_pterygoid_m':'medial_pterygoid_l',
    'rt_medial_pterygoid_m':'medial_pterygoid_r',
    'pterygoid_med_l': 'medial_pterygoid_l',
     'pterygoid_med_r': 'medial_pterygoid_l',
    'lt myelohyoid': 'mylohyoid_l',
    'rt myelohyoid': 'mylohyoid_r',
    'lt_buccinator_m': 'buccinator_l',
    'rt_buccinator_m': 'buccinator_r',
    'lt_masseter_m':'masseter_l',
    'rt_masseter_m':'masseter_r',
    'lt_post_digastric_m':'post_digastric_l',
    'rt_post_digastric_m':'post_digastric_r',
    'lt_sternocleidomastoid_m': 'sternocleidomastoid_l',
    'lt_sternocleidomastoid_m':'sternocleidomastoid_l',
    'rt_sternocleidomastoid_m':'sternocleidomastoid_r',
    'i-smg': 'sternocleidomastoid_l',
        'c-smg': 'sternocleidomastoid_l',
    'lt_thryoid_lobe':'thyroid',
    'rt_thyroid_lobe': 'thyroid',#im just merging all thyroid stuff
    'bone_mandible': 'mandible',
    'musc_buccinat_l':'buccinator_l',
    'musc_buccinat_r':'buccinator_r',
    'musc_geniogloss':'genioglossus_m',
    'musc_digastric_la': 'ant_digastric_l',
    'musc_digastric_lp': 'post_digastric_l',
    'musc_digastric_ra': 'ant_digastric_r',
    'musc_digastric_rp': 'post_digastric_r',
    'musc_masseter_l': 'masseter_l',
    'musc_masseter_r':'masseter_r',
    'musc_mghcomplex': 'mylogeniohyoid',
    'musc_sclmast_l':'sternocleidomastoid_l',
    'musc_sclmast_r': 'sternocleidomastoid_r',
    'mylogeniohyoid_m': 'mylogeniohyoid',
    'mylohyoid_m': 'mylogeniohyoid',
    'oralcavity': 'oral_cavity',
    'palate_soft': 'soft_palate',
    'softpalate': 'soft_palate',
    'soft palate': 'soft_palate',
    'soft_palate1': 'soft_palate',
    'smg_l': 'glnd_submand_l',
    'smg_r':'glnd_submand_r',
    'spinal cord': 'spinal_cord',
    'spinalcord': 'spinal_cord',
    'submandibula_l':'glnd_submand_l',
    'submandibula_r':'glnd_submand_r',
    'submandibular_l':'glnd_submand_l',
    'submandibular_r':'glnd_submand_r',
    'submnd_salv_l': 'glnd_submand_l',
    'submnd_salv_r': 'glnd_submand_r',
    'submand_salv_l1': 'glnd_submand_l',
    'submand_salv_r1':'glnd_sumband_r',
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
}
