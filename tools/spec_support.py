"""Offline support for the repository examples, not a conforming Markdown parser.

This scanner checks directive/attribute structure and the sample's simple rule
lines. CommonMark inline/block conformance requires independent implementations.
"""
import copy
import json
import math
import re
from pathlib import Path
import yaml
from build_registry import KINDS, COMMON, KEYWORDS

class CoreLoader(yaml.SafeLoader):
    pass
CoreLoader.yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)
for ch, rules in CoreLoader.yaml_implicit_resolvers.items():
    CoreLoader.yaml_implicit_resolvers[ch] = [(tag, rx) for tag,rx in rules if not tag.endswith((':bool', ':timestamp', ':int', ':float'))]
CoreLoader.add_implicit_resolver('tag:yaml.org,2002:bool', re.compile(r'^(?:true|True|TRUE|false|False|FALSE)$'), list('tTfF'))
CoreLoader.add_implicit_resolver('tag:yaml.org,2002:int', re.compile(r'^[-+]?[0-9]+$'),list('-+0123456789'))
CoreLoader.add_constructor('tag:yaml.org,2002:int',lambda loader,node:int(loader.construct_scalar(node),10))
CoreLoader.add_implicit_resolver('tag:yaml.org,2002:float', re.compile(r'^[-+]?(?:[0-9]+\.[0-9]*|\.[0-9]+|[0-9]+[eE][-+]?[0-9]+)(?:[eE][-+]?[0-9]+)?$'), list('-+.0123456789'))
def mapping(loader,node,deep=False):
    result={}
    for key,value in node.value:
        k=loader.construct_object(key,deep=deep)
        if not isinstance(k,str) or k in result:raise ValueError('Duplicate or non-string YAML key')
        result[k]=loader.construct_object(value,deep=deep)
    return result
CoreLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
def load_yaml(text):
    for token in yaml.scan(text):
        if isinstance(token,(yaml.tokens.AnchorToken,yaml.tokens.AliasToken,yaml.tokens.TagToken)):
            raise ValueError('YAML anchors, aliases and custom tags are forbidden')
    value=yaml.load(text,Loader=CoreLoader)
    def check(v):
        if isinstance(v,float) and not math.isfinite(v):raise ValueError('Non-finite number')
        if isinstance(v,dict):
            for x in v.values():check(x)
        if isinstance(v,list):
            for x in v:check(x)
    check(value);return value

def attrs(text,kind,extension_props=None):
    if not text:return {}
    if not text.startswith('{') or not text.endswith('}'):raise ValueError('Invalid attribute boundary')
    text=text[1:-1];i=0;result={};classes=[]
    props={**COMMON,**KINDS.get(kind,{}).get('attributes',{}),**(extension_props or {})}
    while i<len(text):
        while i<len(text) and text[i] in ' \t':i+=1
        if i==len(text):break
        if text[i] in '#.':
            prefix=text[i];i+=1;m=re.match(r'[A-Za-z0-9][A-Za-z0-9._-]*',text[i:])
            if not m:raise ValueError('Invalid shorthand')
            val=m.group();i+=len(val)
            if prefix=='.':classes.append(val);continue
            key='id'
        else:
            m=re.match(r'[a-z][a-z0-9_.-]*',text[i:])
            if not m:raise ValueError('Invalid attribute key')
            key=m.group();i+=len(key);val=True
            if i<len(text) and text[i]=='=':
                i+=1
                if i<len(text) and text[i]=='"':val,used=json.JSONDecoder().raw_decode(text[i:]);i+=used
                else:
                    m=re.match(r'[^\s{}"]+',text[i:])
                    if not m:raise ValueError('Missing attribute value')
                    val=m.group();i+=len(val)
        if key in result:raise ValueError('Repeated attribute')
        typ=props.get(key,{}).get('type')
        if typ=='boolean' and isinstance(val,str):
            if val not in ('true','false'):raise ValueError('Invalid boolean')
            val=val=='true'
        elif typ in ('integer','number') and isinstance(val,str):
            if not re.fullmatch(r'-?[0-9]+'+(r'(?:\.[0-9]+)?' if typ=='number' else ''),val):raise ValueError('Invalid number')
            val=float(val) if '.' in val else int(val)
        elif typ=='array' and isinstance(val,str):
            val=[s.strip(' ') for s in val.split(',')]
            if any(not s for s in val):raise ValueError('Empty list member')
        result[key]=val
        if i<len(text) and text[i] not in ' \t':raise ValueError('Attributes require whitespace')
    if classes:
        if 'class' in result:raise ValueError('Repeated class')
        result['class']=classes
    return result

RULE = re.compile(r'^(?:[-*+]\s+|[0-9]+[.)]\s+)?(\*\*)?('+ '|'.join(sorted(KEYWORDS,key=len,reverse=True))+r')(?:\[([A-Za-z0-9][A-Za-z0-9._-]*)\])?(?: \(if ([^()]+)\))?:(\*\*)?\s+(.+)$')
OPEN=re.compile(r'^(:{2,})([a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)?)(\{.*\})?[ \t]*$')
CLOSE=re.compile(r'^(:{3,})[ \t]*$')
CODE=re.compile(r'^\s*(`{3,}|~{3,})(.*)$')
def scan_sample(source,uri='',catalog=None):
    lines=source.splitlines(keepends=True);front={};back={};start=0
    if lines and lines[0].rstrip('\r\n')=='---':
        stop=next((i for i in range(1,len(lines)) if lines[i].rstrip('\r\n')=='---'),None)
        if stop is None:raise ValueError('Unclosed front matter')
        front=load_yaml(''.join(lines[1:stop]));start=stop+1
        if not isinstance(front,dict):raise ValueError('Front matter must be a mapping')
    root=[];stack=[];code=None;comment=False;html_end=None
    def append(text,line):
        arr=stack[-1]['node'].setdefault('children',[]) if stack else root
        if arr and arr[-1]['type']=='markdown':arr[-1]['source']+=text
        else:arr.append({'type':'markdown','source':text,'range':{'start':line,'end':line}})
        arr[-1]['range']['end']=line
    def emit(node):
        (stack[-1]['node'].setdefault('children',[]) if stack else root).append(node)
    for index in range(start,len(lines)):
        raw=lines[index];line=raw.rstrip('\r\n');n=index+1
        if stack and stack[-1]['opaque']:
            cur=stack[-1];m=CLOSE.fullmatch(line)
            if m and len(m[1])>=cur['length']:
                stack.pop();node=cur['node'];node['range']['end']=n
                text=''.join(cur['raw']);fmt=cur['format']
                if fmt=='markdown':node['children']=[{'type':'markdown','source':text}]
                else:
                    node['value']={'format':fmt,'source':text}
                    if fmt in ('yaml','json'):node['value']['data']=load_yaml(text) if fmt=='yaml' else json.loads(text,object_pairs_hook=unique_json)
                continue
            cur['raw'].append(raw);continue
        if html_end:
            append(raw,n)
            if re.search(html_end,line,re.I):html_end=None
            continue
        if code:
            append(raw,n)
            if re.fullmatch(re.escape(code[0])+r'{'+str(code[1])+r',}[ \t]*',line.lstrip()):code=None
            continue
        m=CODE.match(line)
        if m:
            code=(m[1][0],len(m[1]));append(raw,n);continue
        if comment:
            if '-->' in line:
                comment=False;tail=line.split('-->',1)[1]
                if tail:append(tail+'\n',n)
            continue
        if '<!--' in line:
            before,after=line.split('<!--',1)
            if '-->' in after:
                text=before+after.split('-->',1)[1]
                if text:append(text+'\n',n)
            else:
                comment=True
                if before:append(before+'\n',n)
            continue
        if not stack:
            html=re.match(r'^<(script|pre|style|textarea)(?:[ \t>]|$)',line,re.I)
            terminator=(r'</'+html[1]+r'\s*>' if html else
                        r'\?>' if line.startswith('<?') else
                        r'\]\]>' if line.startswith('<![CDATA[') else
                        r'>' if re.match(r'^<![A-Z]',line) else None)
            if terminator:
                append(raw,n)
                if not re.search(terminator,line,re.I):html_end=terminator
                continue
        if line=='---' and not stack and index>start and not lines[index-1].strip():
            # Plain thematic breaks stay Markdown unless a known first key
            # explicitly cues terminal backmatter. YAML errors then stay errors.
            following=next((s.rstrip('\r\n') for s in lines[index+1:]
                            if s.strip() and not s.lstrip().startswith('#')), '')
            if re.match(r'^(?:authors|owners|review|history|sources|approvals|notes|test_results):(?:[ \t]|$)',following):
                back=load_yaml(''.join(lines[index+1:]))
                if not isinstance(back,dict):raise ValueError('Backmatter must be a mapping')
                break
        m=CLOSE.fullmatch(line)
        if m and stack:
            if len(m[1])<stack[-1]['length']:raise ValueError('Short closing fence')
            cur=stack.pop();cur['node']['range']['end']=n;continue
        m=OPEN.fullmatch(line)
        if m:
            fence,kind,at=m.groups()
            descriptor=None
            if ':' in kind:
                alias,local=kind.split(':',1);binding=front.get('extensions',{}).get(alias,{})
                manifest=(catalog or {}).get(binding.get('id'),{})
                descriptor=manifest.get('provides',{}).get('blocks',{}).get(local)
            a=attrs(at,kind,descriptor.get('attributes',{}) if descriptor else None)
            node={'type':'directive','kind':kind,'form':'leaf' if len(fence)==2 else 'container','attrs':a,'range':{'start':n,'end':n}}
            if kind not in KINDS and ':' not in kind:raise ValueError('unknown-kind: '+kind)
            if len(fence)==2:emit(node);continue
            if stack and len(fence)>=stack[-1]['length']:raise ValueError('invalid-nesting')
            fmt=a.get('format',(KINDS.get(kind) or descriptor or {}).get('body','markdown'))
            opaque=fmt!='markdown' or kind=='example' or a.get('verbatim',False) or (kind not in KINDS and not descriptor)
            if not opaque:node['children']=[]
            emit(node);stack.append({'node':node,'length':len(fence),'opaque':opaque,'format':fmt,'raw':[]});continue
        m=RULE.fullmatch(line)
        if m:
            bold,key,id_,condition,close,text=m.groups()
            if bool(bold)!=bool(close):raise ValueError('Unmatched rule emphasis')
            a={};kind=KEYWORDS[key]
            if id_:a['id']=id_
            if condition:a['if']=condition
            if key in ('SHOULD NOT','AVOID'):a['not']=True
            emit({'type':'directive','kind':kind,'form':'keyword','attrs':a,'children':[{'type':'markdown','source':text+'\n'}],'range':{'start':n,'end':n}});continue
        if line.startswith('BECAUSE: '):
            arr=stack[-1]['node']['children'] if stack else root
            if arr and arr[-1]['type']=='directive' and arr[-1]['kind'] in ('must','never','should','may','guardrail'):
                if 'because' in arr[-1]['attrs']:raise ValueError('reason-repeated')
                arr[-1]['attrs']['because']=line[9:];continue
        append(raw,n)
    if stack:raise ValueError('unclosed-directive')
    result={'format':'instruction/1','metadata':{'front':front,'back':back},'body':root}
    if uri:result['uri']=uri
    return result

def unique_json(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ValueError('Duplicate JSON key')
        result[k]=v
    return result

def walk(nodes,parent=None):
    for node in nodes:
        yield node,parent
        yield from walk(node.get('children',[]),node)

def model_errors(document):
    errors=[];ids=set()
    for n,parent in walk(document['body']):
        a=n.get('attrs',{});id_=a.get('id')
        identity=(n.get('instance','root'),id_)
        if id_:
            if identity in ids:errors.append('duplicate-id')
            ids.add(identity)
        if n['type']=='directive':
            kind=n['kind'];d=KINDS.get(kind)
            if not d and ':' not in kind:errors.append('unknown-kind')
            if d and d.get('parent') and (not parent or parent.get('kind')!=d['parent']):errors.append('invalid-nesting')
            if a.get('mode')=='pinned' and not a.get('sha256'):errors.append('pin-mismatch')
            if a.get('end',1)<=a.get('start',0):errors.append('invalid-attributes')
            if n.get('value',{}).get('format') in ('yaml','json') and kind not in ('data',):
                if not isinstance(n['value'].get('data'),dict):errors.append('invalid-structured-body')
    return errors

def text_profile(doc):
    def render(nodes):
        units=[]
        for n in nodes:
            if n['type']=='markdown':units.append(n['source'].replace('\r\n','\n').replace('\r','\n').strip('\n'));continue
            k=n['kind'];a=n['attrs'];title=a.get('title',a.get('id',k))
            child=(''.join(x.get('source','') for x in n.get('children',[])).strip('\n')) if (k=='example' or a.get('verbatim')) else render(n.get('children',[]))
            if k in ('must','never','should','may','guardrail','always','avoid'):
                label={'must':'MUST','always':'MUST','never':'NEVER','should':'SHOULD','avoid':'SHOULD NOT','may':'MAY','guardrail':'GUARDRAIL'}[k]
                if k=='should' and a.get('not'):label='SHOULD NOT'
                if a.get('if'):label+=' (if '+a['if']+')'
                t=label+': '+child
                if a.get('because'):t+='\nBECAUSE: '+a['because']
                units.append(t);continue
            label={'policy':'Policy','instruction':'Instruction','context':'Context','example':'Counterexample' if a.get('avoid') else 'Example'}.get(k,k)
            t='### '+label+': '+title
            excluded={'id','title','class','style'}
            if KINDS.get(k,{}).get('family')=='layout':excluded.update(('count','columns','span','open'))
            values={x:y for x,y in a.items() if x not in excluded}
            if k=='example':values.pop('avoid',None)
            if values:
                t+='\n\nAttributes: '+json.dumps(values,ensure_ascii=False,sort_keys=True,separators=(',',':'))
            if 'value' in n:
                v=n['value'];t+='\n\n'+fence(v['source'],v['format'])
            elif k=='example':t+='\n\n'+fence(child,'markdown')
            elif child:t+='\n\n'+child
            units.append(t)
        return '\n\n'.join(u for u in units if u)
    text=render(doc['body'])
    records=sorted(doc.get('objects',[])+doc.get('resources',[]),key=lambda x:x['key'])
    if records:
        text+='\n\n### Resolved references\n\n'+'\n\n'.join(fence(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')),'json') for r in records)
    changes=[p for p in doc.get('provenance',[]) if p.get('operation') in ('replace','extend','remove')]
    if changes:
        text+='\n\n### Composition changes\n\n'+'\n'.join('- '+c['operation']+' '+c['target']+' (origin: '+c['uri']+')'+(' — '+c['reason'] if c.get('reason') else '') for c in changes)
    return text.rstrip('\n')+'\n'

def fence(text,lang):
    runs=re.findall(r'`+',text);marker='`'*max(3,max((len(x)+1 for x in runs),default=3))
    return marker+lang+'\n'+text+('' if text.endswith('\n') else '\n')+marker

def compose_fixture(document, documents, trail=(), instance='root'):
    """Composition of pre-parsed fixture trees only; no network or general URI resolver."""
    key=document.get('uri','root')
    if key in trail:raise ValueError('composition-cycle')
    tree=copy.deepcopy(document);front=tree.get('metadata',{}).get('front',{})
    inherited=[];provenance=[]
    def import_document(ref,alias,operation):
        target=ref['uri'];path,sep,fragment=target.partition('#')
        if path not in documents:raise ValueError('reference-missing')
        result,origins=compose_fixture(documents[path],documents,trail+(key,),instance+'/'+alias)
        selected=result['body']
        selector=ref.get('select',{}).get('id') or (fragment.removeprefix('id=') if sep else None)
        if selector:
            selected=select_id(selected,selector)
            if selected is None:raise ValueError('reference-missing')
        provenance.extend(origins)
        provenance.append({'instance':instance+'/'+alias,'uri':documents[path].get('uri',path),'operation':operation})
        return selected
    aliases=set()
    for base in front.get('extends',[]):
        alias=base['as']
        if alias in aliases:raise ValueError('duplicate-id')
        aliases.add(alias);inherited.extend(import_document(base,alias,'inherit'))
    local=[]
    for node in tree['body']:
        if node['type']!='directive' or node['kind'] not in ('replace','extend','remove'):
            local.append(stamp(node,instance));continue
        target=node['attrs']['target'].lstrip('#');parts=target.split('/')
        if len(parts)<2:raise ValueError('patch-target')
        wanted_instance=instance+'/'+ '/'.join(parts[:-1]);wanted_id=parts[-1]
        location=find_id(inherited,wanted_instance,wanted_id)
        if location is None:raise ValueError('patch-target')
        parent,index=location;original=copy.deepcopy(parent[index]);op=node['kind']
        if op=='remove':parent.pop(index)
        elif op=='replace':
            dest=parent[index]
            if 'value' in original:
                if node.get('value',{}).get('format')!=original['value']['format']:raise ValueError('patch-body')
                dest['value']=copy.deepcopy(node['value']);dest.pop('children',None)
            else:
                if 'value' in node:raise ValueError('patch-body')
                dest['children']=[stamp(n,instance) for n in node.get('children',[])]
        else:
            if 'value' in original:raise ValueError('patch-body')
            children=[stamp(n,instance) for n in node.get('children',[])]
            dest=parent[index];dest['children']=(children+dest.get('children',[])) if node['attrs'].get('position')=='prepend' else (dest.get('children',[])+children)
        provenance.append({'instance':wanted_instance,'uri':key,'operation':op,'target':target,'reason':node['attrs'].get('reason',''),'original':original,'modified_by':key})
    def includes(nodes):
        result=[]
        for node in nodes:
            if node['type']=='directive' and node['kind']=='include':
                a=node['attrs'];alias=a['as']
                if alias in aliases:raise ValueError('duplicate-id')
                aliases.add(alias);result.extend(import_document({'uri':a['src']},alias,'include'))
            else:
                if 'children' in node:node['children']=includes(node['children'])
                result.append(node)
        return result
    tree['body']=inherited+includes(local)
    return tree,provenance

def stamp(node,instance):
    node=copy.deepcopy(node);node['instance']=instance
    if 'children' in node:node['children']=[stamp(n,instance) for n in node['children']]
    return node

def find_id(nodes,instance,id_):
    for index,node in enumerate(nodes):
        if node.get('instance')==instance and node.get('attrs',{}).get('id')==id_:return nodes,index
        found=find_id(node.get('children',[]),instance,id_)
        if found:return found
    return None

def select_id(nodes,id_):
    for node in nodes:
        if node.get('attrs',{}).get('id')==id_:return [copy.deepcopy(node)]
        found=select_id(node.get('children',[]),id_)
        if found:
            if node.get('kind')=='policy':
                wrapper=copy.deepcopy(node);wrapper['children']=found;return [wrapper]
            return found
    return None
