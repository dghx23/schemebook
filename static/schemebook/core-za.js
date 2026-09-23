(function(global){"use strict";
const schemes=(global.SCHEMEBOOK_DATA&&global.SCHEMEBOOK_DATA.schemes)||[];
const sourceClasses=[
  {id:"registry",label:"CMS registration record",purpose:"Registration status, scheme type and canonical identity"},
  {id:"rules",label:"Registered scheme rules",purpose:"Membership, benefits, exclusions, disputes and governance"},
  {id:"options",label:"Benefit option documents",purpose:"Benefits, limits, tariffs, co-payments and contributions by year"},
  {id:"networks",label:"Provider network and DSP lists",purpose:"Hospitals, professionals, pharmacies and PMB pathways"},
  {id:"formularies",label:"Medicine formularies and protocols",purpose:"Funded medicines, clinical rules and exception routes"},
  {id:"forms",label:"Member forms and process guides",purpose:"Authorisation, chronic registration, claims and appeals"},
  {id:"notices",label:"Current notices and circulars",purpose:"Document changes, effective dates and member communications"}
];
const records=Object.fromEntries(schemes.map(s=>[s.slug,{
  scheme_slug:s.slug,
  scheme_name:s.name,
  scheme_type:s.type,
  ingestion_status:"awaiting_source_pack",
  coverage_status:"registry_only",
  last_verified_at:null,
  source_documents:[],
  extracted_facts:[],
  answerable_topics:[],
  review:{status:"not_started",reviewed_by:null,reviewed_at:null},
  provenance:{canonical_registry:"CMS Industry Report 2023",source_urls:[],content_hashes:[]}
}]));
global.SCHEMEBOOK_CORE_ZA={
  contract:"core-za.scheme-knowledge.v1",
  mode:"placeholder",
  generated_for:schemes.length,
  shared_reference_layers:[
    {id:"schemes",label:"Registered schemes",count:71,note:"16 open · 55 restricted",status:"available",route:"/core/za/medical-schemes/schemes"},
    {id:"pmb",label:"PMB sections",count:6,note:"minimum benefit framework",status:"shared_reference",route:"/core/za/medical-schemes/pmb"},
    {id:"cdl",label:"Chronic Disease List",count:26,note:"listed chronic conditions",status:"shared_reference",route:"/core/za/medical-schemes/cdl"},
    {id:"dtp",label:"Diagnosis Treatment Pairs",count:266,note:"diagnosis and minimum treatment pairs",status:"shared_reference",route:"/core/za/medical-schemes/dtp"}
  ],
  source_classes:sourceClasses,
  records,
  ingestion_policy:{
    preferred_methods:["official API or structured feed","permitted site retrieval","document download and text extraction","OCR for image-only documents","manual source upload"],
    safeguards:["official and first-party sources first","respect access controls, robots rules, terms and rate limits","retain source URL, document date, retrieval time and content hash","separate extraction from human review","never answer beyond verified source coverage"],
    promotion_flow:["discover","retrieve","extract","normalise","validate","human review","publish to Sentrix SchemeBook copy","promote to SchemeBook actual"]
  }
};
})(typeof window!=="undefined"?window:globalThis);
