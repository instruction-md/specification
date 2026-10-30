#!/usr/bin/env python3
"""Build the normative registry and interchange schemas. No network access."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = 'https://json-schema.org/draft/2020-12/schema'
BASE = 'https://instruction.md/specification/1/'
ID = r'^[A-Za-z0-9][A-Za-z0-9._-]*$'
KIND = r'^[a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)?$'
DIGEST = r'^sha256:[0-9a-f]{64}$'
S = {'type': 'string'}
B = {'type': 'boolean'}
I = {'type': 'integer'}
N = {'type': 'number'}
LS = {'type': 'array', 'items': S}
def enum(*values): return {'enum': list(values)}
def obj(props, required=(), extra=False):
    return {'type':'object', 'properties':props, 'required':list(required), 'additionalProperties':extra}
def bounded(lo, hi): return {'type':'integer', 'minimum':lo, 'maximum':hi}
COMMON = {
    'id': {'type':'string', 'pattern': ID}, 'title':{'type':'string','pattern':r'^[^\r\n]*$'}, 'class':LS,
    'format': enum('markdown','yaml','json','csv','text','html','code'),
    'verbatim':B, 'src':S, 'ref':S, 'mode':enum('live','pinned'), 'version':S,
    'sha256':{'type':'string','pattern':DIGEST}, 'required':B,
    'description':S, 'style':S,
}
KINDS = {}
def add(names, body='markdown', forms=('container',), attrs=None, required=(), family='guidance', **more):
    for name in names.split():
        KINDS[name] = {'body':body, 'forms':list(forms), 'attributes': attrs or {},
                       'required':list(required), 'family':family, **more}
RULE = {'if':{'type':'string','pattern':r'^[^()\r\n]+$'}, 'because':S}
add('must never guardrail', attrs=RULE, forms=('container','keyword','alert'))
add('should', attrs={**RULE,'not':B}, forms=('container','keyword','alert'))
add('may',attrs=RULE,forms=('container','keyword','alert'))
add('always',attrs=RULE,forms=('container','keyword','alert'),alias='must')
add('avoid',attrs=RULE,forms=('container','keyword','alert'),alias='should',flags={'not':True})
add('note tip important warning caution',forms=('container','keyword','alert'),family='advisory')
add('info',forms=('container','keyword','alert'),family='advisory',alias='note')
add('example',attrs={'avoid':B},family='advisory',opaque=True)
add('instruction context')
add('policy',attrs={'scope':S,'authority':S,'source':S})
add('output',attrs={'response-format':S,'schema':S},family='contract')
add('form',family='contract')
PARAM = {'name':{'type':'string','pattern':r'^[A-Za-z_][A-Za-z0-9_.-]*$'},
         'type':enum('string','number','integer','boolean','enum','list','url','duration'),
         'values':LS,'default':{},'example':{},'source':enum('input','workspace','identity','static'),
         'required':B,'description':S}
add('param',body='none',forms=('leaf',),attrs=PARAM,required=('name',),family='contract')
add('glossary',family='contract')
add('person',forms=('container','leaf'),attrs={'role':S,'resolver':S,'account':S},required=('id',),family='connected')
add('role',forms=('container','leaf'),attrs={'resolver':S,'account':S},required=('id',),family='connected')
add('skill',forms=('container','leaf'),attrs={'trigger':S,'resolver':S},required=('id',),family='connected')
add('mcp',forms=('container','leaf'),attrs={'registry':S,'server':S,'account':S,'tools':LS,'allow':LS,'deny':LS,'resolver':S},required=('id',),family='connected')
add('tool',forms=('container','leaf'),attrs={'server':S,'name':S,'allow':LS,'deny':LS},required=('id','server','name'),family='connected')
add('agent',forms=('container','leaf'),attrs={'protocol':S,'resolver':S,'account':S},required=('id',),family='connected')
add('service source',forms=('container','leaf'),attrs={'resolver':S,'account':S,'media-type':S},required=('id',),family='connected')
MEDIA = {'media-type':S,'alt':S,'caption':S,'transcript':S,'preview':S,'decorative':B,
         'page':{'type':'integer','minimum':1},'start':{'type':'integer','minimum':0},
         'end':{'type':'integer','minimum':0},'region':S}
add('resource image audio video pdf diagram drawing',forms=('container','leaf'),attrs=MEDIA,family='resource')
add('figure',attrs=MEDIA,family='resource')
add('script',attrs={'lang':S,'sandbox':S,'entry':S},required=('id',),family='technical')
add('data',body='yaml',attrs={'schema':S},required=('id',),family='technical',formats=['yaml','json','csv','text'])
add('schedule workflow sandbox test eval',body='yaml',attrs={'dialect':S,'adapter':S,'target':S},required=('id',),family='technical',formats=['yaml','json'])
KINDS['schedule']['required']=['id','dialect']
KINDS['workflow']['required']=['id','dialect']
add('config',body='yaml',attrs={'dialect':S,'adapter':S,'target':S},required=('id','dialect'),family='technical',formats=['yaml','json'])
for runtime_kind in ('config','workflow','schedule'):
    KINDS[runtime_kind]['attributes'].update({'schema':S,'schema-sha256':{'type':'string','pattern':DIGEST}})
add('properties',body='yaml',attrs={'patch':B},family='technical',formats=['yaml','json'])
add('section columns column grid card tabs tab steps step details aside',family='layout')
KINDS['columns']['attributes']={'count':bounded(1,12)}
KINDS['column']['attributes']={'span':bounded(1,12)}
KINDS['column']['parent']='columns'
KINDS['grid']['attributes']={'columns':bounded(1,12)}
KINDS['tab']['parent']='tabs'; KINDS['step']['parent']='steps'
KINDS['details']['attributes']={'open':B}
add('component',attrs={'component':S,'stylesheet':S},required=('component',),family='presentation')
add('include',body='none',forms=('leaf',),attrs={'as':{'type':'string','pattern':ID}},required=('src','as'),family='composition')
add('embed',forms=('container','leaf'),attrs=MEDIA,required=('src',),family='composition')
add('replace',attrs={'target':S,'reason':S},required=('target',),family='composition',formats=['markdown','yaml','json'])
add('extend',attrs={'target':S,'reason':S,'position':enum('prepend','append')},required=('target',),family='composition')
add('remove',body='none',forms=('leaf',),attrs={'target':S,'reason':S},required=('target',),family='composition')
INLINES = {k:{'ref':S} for k in 'ref person role skill mcp tool agent service source resource cite'.split()}
INLINES.update({k:{} for k in 'mark sub sup kbd icon badge'.split()})
INLINES['abbr']={'title':S}; INLINES['button']={'href':S}
KEYWORDS = {'MUST':'must','MUST NOT':'never','NEVER':'never','ALWAYS':'must',
 'SHOULD':'should','SHOULD NOT':'should','AVOID':'should','MAY':'may','GUARDRAIL':'guardrail',
 'NOTE':'note','INFO':'note','TIP':'tip','IMPORTANT':'important','WARNING':'warning','CAUTION':'caution'}

def attributes(kind):
    d=KINDS[kind]
    return {**obj({**COMMON,**d['attributes']},d['required']),
            'patternProperties':{'^x-[a-z0-9_.-]+$':{}}}

def documents():
    registry={'format':'instruction-registry/1','spec':'1','common_attributes':COMMON,
              'kinds':dict(sorted(KINDS.items())),'inline':INLINES,'keywords':KEYWORDS,
              'keyword_flags':{'SHOULD NOT':{'not':True},'AVOID':{'not':True}},
              'grammar':{'kind':KIND,'id':ID,'parameter':r'^[A-Za-z_][A-Za-z0-9_.-]*$',
                         'digest':DIGEST}}
    ref=obj({'uri':S,'select':{'$ref':'#/$defs/selector'},'mode':enum('live','pinned'),
             'version':S,'sha256':{'type':'string','pattern':DIGEST},'required':B,
             'as':{'type':'string','pattern':ID},'with':{'type':'object'}},('uri',))
    ref['allOf']=[{'if':{'properties':{'mode':{'const':'pinned'}},'required':['mode']},'then':{'required':['sha256']}}]
    selector={'oneOf':[
      obj({'id':S},('id',)),obj({'heading':S,'occurrence':{'type':'integer','minimum':1}},('heading',)),
      obj({'lines':{'type':'array','prefixItems':[{'type':'integer','minimum':1}]*2,'minItems':2,'maxItems':2}},('lines',)),
      obj({'pointer':{'type':'string','pattern':r'^(?:/(?:[^~]|~[01])*)*$'}},('pointer',)),
      obj({'page':{'type':'integer','minimum':1}},('page',)),
      obj({'time':{'type':'array','items':{'type':'integer','minimum':0},'minItems':2,'maxItems':2}},('time',)),
      obj({'region':{'type':'array','items':{'type':'number','minimum':0,'maximum':1},'minItems':4,'maxItems':4}},('region',))]}
    param=obj(PARAM)
    param['allOf']=[{'if':{'properties':{'type':{'const':'enum'}},'required':['type']},'then':{'required':['values'],'properties':{'values':{'type':'array','items':S,'minItems':1}}}}]
    front=obj({'spec':enum('1',1),'id':S,'version':S,'title':S,'description':S,'language':S,'license':S,'tags':LS,
      'parameters':{'type':'object','propertyNames':{'pattern':r'^[A-Za-z_][A-Za-z0-9_.-]*$'},'additionalProperties':param},
      'extends':{'type':'array','items':{'allOf':[ref,{'required':['as']}]}},
      'references':{'type':'object','additionalProperties':ref},
      'extensions':{'type':'object','propertyNames':{'pattern':r'^[a-z][a-z0-9-]*$'},'additionalProperties':obj({'id':S,'version':S,'required':B,'manifest':S,'sha256':{'type':'string','pattern':DIGEST}},('id','version'))},
      'resolvers':{'type':'object','additionalProperties':obj({'adapter':S,'account':S},('adapter',),True)},
      'exports':{'type':'object','propertyNames':{'pattern':ID},'additionalProperties':obj({'adapter':S,'profile':S,'bindings':{'type':'object'},'required':B},('adapter','profile','bindings'))},
      'presentation':{'type':'object'},'requires':LS},extra=True)
    range_=obj({'start':{'type':'integer','minimum':1},'end':{'type':'integer','minimum':1}},('start','end'))
    value=obj({'format':enum('yaml','json','csv','text','html','code'),'source':S,'data':{}},('format','source'))
    markdown=obj({'type':{'const':'markdown'},'source':S,'range':{'$ref':'#/$defs/range'},'instance':S,'attrs':obj({'id':{'type':'string','pattern':ID}})},('type','source'))
    directive=obj({'type':{'const':'directive'},'kind':{'type':'string','pattern':KIND},
       'form':enum('container','leaf','keyword','alert'),'attrs':{'type':'object'},
       'children':{'type':'array','items':{'$ref':'#/$defs/node'}},'value':{'$ref':'#/$defs/value'},
       'source':S,'instance':S,'range':{'$ref':'#/$defs/range'}},('type','kind','form','attrs'))
    directive['allOf']=[{'not':{'required':['children','value']}}]
    for name,d in KINDS.items():
        cond={'if':{'properties':{'kind':{'const':name}},'required':['kind']},
              'then':{'properties':{'attrs':attributes(name),'form':{'enum':d['forms']}}}}
        if d['body']=='none':
            cond['then']['not']={'anyOf':[{'required':['children']},{'required':['value']}]}
        elif d['body']=='yaml':
            cond['then']['if']={'properties':{'form':{'const':'container'}}}
            cond['then']['then']={'required':['value'],'properties':{'value':{'properties':{'format':{'enum':d.get('formats',['yaml','json'])}}}}}
        else:
            formats=d.get('formats',['markdown'])
            cond['then']['properties']['attrs']['properties']['format']={'enum':formats}
            if len(formats)>1:
                cond['then']['if']={'properties':{'attrs':{'properties':{'format':{'enum':[f for f in formats if f!='markdown']}},'required':['format']}}}
                cond['then']['then']={'required':['value']}
                cond['then']['else']={'required':['children']}
            else:
                cond['then']['if']={'properties':{'form':{'enum':['container','keyword','alert']}}}
                cond['then']['then']={'required':['children']}
        if name=='param':cond['then']['properties']['attrs']['allOf']=param['allOf']
        directive['allOf'].append(cond)
    authored={'$schema':DRAFT,'$id':BASE+'instruction.schema.json','title':'Instruction authored document',
       **obj({'format':{'const':'instruction/1'},'uri':S,'metadata':obj({'front':front,'back':{'type':'object'}}),
              'body':{'type':'array','items':{'$ref':'#/$defs/node'}}},('format','body')),
       '$defs':{'range':range_,'value':value,'node':{'oneOf':[markdown,directive]},'selector':selector,'reference':ref}}
    diagnostic=obj({'code':S,'severity':enum('error','warning','info'),'message':S,'uri':S,'range':range_,'target':S,'remedy':S},('code','severity','message'))
    dependency=obj({'uri':S,'resolved_uri':S,'sha256':{'type':'string','pattern':DIGEST},'mode':enum('live','pinned'),
                    'version':S,'selector':selector,'instance':S,'extensions':{'type':'object'}},('uri','resolved_uri','sha256','mode','instance'))
    origin=obj({'instance':S,'uri':S,'range':range_,'selector':selector,'operation':enum('include','inherit','replace','extend','remove'),
                'target':S,'reason':S,'modified_by':S,'original':{}},('instance','uri'))
    record=obj({'key':S,'kind':S,'label':S,'target':S,'status':enum('resolved','unresolved'),
                'data':{},'source':S,'sha256':{'type':'string','pattern':DIGEST}},('key','kind','label','target','status'))
    resolved={'$schema':DRAFT,'$id':BASE+'schemas/resolved.schema.json','title':'Resolved instruction snapshot',
      **obj({'format':{'const':'instruction-resolved/1'},'status':enum('complete','partial'),
       'document':obj({'uri':S,'sha256':{'type':'string','pattern':DIGEST},'version':S},('uri','sha256')),
       'body':{'type':'array','items':{'$ref':'../instruction.schema.json#/$defs/node'}},
       'extensions':{'type':'array','items':obj({'instance':S,'alias':S,'id':S,'version':S,'sha256':{'type':'string','pattern':DIGEST}},('instance','alias','id','version','sha256'))},
       'objects':{'type':'array','items':record},'resources':{'type':'array','items':record},
       'dependencies':{'type':'array','items':dependency},'provenance':{'type':'array','items':origin},
       'diagnostics':{'type':'array','items':diagnostic},'resolved_digest':{'type':'string','pattern':DIGEST}},
       ('format','status','document','body','extensions','objects','resources','dependencies','provenance','diagnostics'))}
    provided=obj({'body':enum('markdown','yaml','json','text','code'),'forms':{'type':'array','items':enum('container','leaf','inline'),'minItems':1,'uniqueItems':True},
       'attributes':{'type':'object'},'fallback':enum('children','source'),'required':LS,'resolved':{'type':'object'},'parents':LS},('body','forms','attributes','fallback'))
    extension={'$schema':DRAFT,'$id':BASE+'schemas/extension.schema.json','title':'Instruction extension manifest',
       **obj({'format':{'const':'instruction-extension/1'},'id':{'type':'string','pattern':r'^[a-z0-9]+(?:[.-][a-z0-9]+)+/[a-z][a-z0-9-]*$'},
        'version':{'type':'string','minLength':1},'spec':{'type':'array','items':{'const':'1'},'minItems':1},
        'roles':{'type':'array','items':enum('syntax','semantic','presentation','resolver','test-adapter'),'minItems':1,'uniqueItems':True},
        'provides':obj({'blocks':{'type':'object','additionalProperties':provided},'inline':{'type':'object','additionalProperties':provided},
                       'resolvers':{'type':'object'},'test_adapters':{'type':'object'},
                       'workflow_nodes':{'type':'object','additionalProperties':obj({'role':enum('trigger','step'),
                           'schema':{'type':'object'},'semantics':S,'requires':LS},('role','schema','semantics'))}},extra=False),
        'dependencies':{'type':'object'},'modules':{'type':'object'},'requires':LS,'license':S},('format','id','version','spec','roles','provides'))}
    path={'type':'string','pattern':r'^(?!/)(?!.*(?:^|/)(?:\.|\.\.)(?:/|$))(?!.*//)(?!.*\\)[^/]+(?:/[^/]+)*$'}
    entry=obj({'path':path,'media_type':S,'sha256':{'type':'string','pattern':DIGEST},'uri':S,'version':S,'mode':enum('live','pinned')},('path','media_type','sha256','uri'))
    export_source=obj({'uri':S,'sha256':{'type':'string','pattern':DIGEST},'select':selector},('uri','sha256'))
    export_=obj({'id':S,'kind':enum('agent-instructions','config','workflow','skill','resource'),'path':path,
      'sha256':{'type':'string','pattern':DIGEST},'adapter':S,'profile':S,'dialect':S,'sources':{'type':'array','items':export_source,'minItems':1}},
      ('id','kind','path','sha256','adapter','profile','sources'))
    bundle={'$schema':DRAFT,'$id':BASE+'schemas/bundle.schema.json','title':'Instruction bundle manifest',
      **obj({'format':{'const':'instruction-bundle/1'},'main':path,'complete':B,
             'entries':{'type':'array','items':entry,'minItems':1},'mapping':{'type':'object','additionalProperties':path},
             'exports':{'type':'array','items':export_}},('format','main','complete','entries','mapping'))}
    request=obj({'format':{'const':'instruction-test-request/1'},'id':S,'document_digest':{'type':'string','pattern':DIGEST},
      'target':S,'adapter':S,'inputs':{},'profile':S,'model':{'type':'object'}},('format','id','document_digest','target','adapter','inputs'))
    result=obj({'format':{'const':'instruction-test-result/1'},'request':S,'document_digest':{'type':'string','pattern':DIGEST},
      'status':enum('passed','failed','error','skipped'),'environment':{'type':'object'},'started':{'type':'string','format':'date-time'},
      'finished':{'type':'string','format':'date-time'},'assertions':{'type':'array','items':obj({'name':S,'status':enum('passed','failed','error','skipped'),'detail':S},('name','status'))},
      'artifacts':{'type':'array','items':ref}},('format','request','document_digest','status','environment','started','finished','assertions','artifacts'))
    testing={'$schema':DRAFT,'$id':BASE+'schemas/testing.schema.json','title':'Instruction test exchange', 'oneOf':[request,result], '$defs':{'selector':selector}}
    from workflow_support import workflow_documents
    return {'registry.json':registry,'instruction.schema.json':authored,'schemas/resolved.schema.json':resolved,
            'schemas/extension.schema.json':extension,'schemas/bundle.schema.json':bundle,'schemas/testing.schema.json':testing,
            **workflow_documents()}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true');args=p.parse_args()
    stale=[]
    for name, value in documents().items():
        data=json.dumps(value,ensure_ascii=False,indent=2)+'\n';path=ROOT/name
        if args.check:
            if not path.exists() or path.read_text()!=data:stale.append(name)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data)
    from workflow_support import workflow_catalog
    catalog_path=ROOT/'reference/workflow-nodes.md'
    if args.check:
        if not catalog_path.exists() or catalog_path.read_text()!=workflow_catalog():stale.append('reference/workflow-nodes.md')
    else:catalog_path.write_text(workflow_catalog())
    if stale:raise SystemExit('Stale generated files: '+', '.join(stale))
    print(('Checked' if args.check else 'Generated')+f' registry ({len(KINDS)} block kinds), workflow registry and 6 schemas.')
if __name__=='__main__':main()
