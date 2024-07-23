import{errors}from"../util.js";const{INVALID:INVALID,GONE:GONE,MISMATCH:MISMATCH,MOD_ERR:MOD_ERR,SYNTAX:SYNTAX}=errors,DIR={headers:{"content-type":"dir"}},FILE=()=>({headers:{"content-type":"file","last-modified":Date.now()}}),hasOwn=Object.prototype.hasOwnProperty;class Sink{constructor(e,t,i){this._cache=e,this.path=t,this.size=i.size,this.position=0,this.file=i}write(e,t){if("object"==typeof e)if("write"===e.type){if(Number.isInteger(e.position)&&e.position>=0&&(this.size<e.position&&(this.file=new Blob([this.file,new ArrayBuffer(e.position-this.size)])),this.position=e.position),!("data"in e))throw new DOMException(...SYNTAX("write requires a data argument"));e=e.data}else{if("seek"===e.type){if(Number.isInteger(e.position)&&e.position>=0){if(this.size<e.position)throw new DOMException(...INVALID);return void(this.position=e.position)}throw new DOMException(...SYNTAX("seek requires a position argument"))}if("truncate"===e.type){if(Number.isInteger(e.size)&&e.size>=0){let t=this.file;return t=e.size<this.size?t.slice(0,e.size):new File([t,new Uint8Array(e.size-this.size)],t.name),this.size=t.size,this.position>t.size&&(this.position=t.size),void(this.file=t)}throw new DOMException(...SYNTAX("truncate requires a size argument"))}}e=new Blob([e]);let i=this.file;const s=i.slice(0,this.position),n=i.slice(this.position+e.size);let a=this.position-s.size;a<0&&(a=0),i=new File([s,new Uint8Array(a),e,n],i.name),this.size=i.size,this.position+=e.size,this.file=i}async close(){const[e]=await this._cache.keys(this.path);if(!e)throw new DOMException(...GONE);return this._cache.put(this.path,new Response(this.file,FILE()))}}export class FileHandle{constructor(e,t){this._cache=t,this.path=e,this.kind="file",this.writable=!0,this.readable=!0}get name(){return this.path.split("/").pop()}async isSameEntry(e){return this.path===e.path}async getFile(){const e=await this._cache.match(this.path);if(!e)throw new DOMException(...GONE);const t=await e.blob();return new File([t],this.name,{lastModified:+e.headers.get("last-modified")})}async createWritable(e){const[t]=await this._cache.keys(this.path);if(!t)throw new DOMException(...GONE);return new Sink(this._cache,this.path,e.keepExistingData?await this.getFile():new File([],this.name))}}export class FolderHandle{constructor(e,t){this._dir=e,this.writable=!0,this.readable=!0,this._cache=t,this.kind="directory",this.name=e.split("/").pop()}async*entries(){for(const[e,t]of Object.entries(await this._tree))yield[e.split("/").pop(),t?new FileHandle(e,this._cache):new FolderHandle(e,this._cache)]}async isSameEntry(e){return this._dir===e._dir}async getDirectoryHandle(e,t){const i=this._dir.endsWith("/")?this._dir+e:`${this._dir}/${e}`,s=await this._tree;if(hasOwn.call(s,i)){if(s[i])throw new DOMException(...MISMATCH);return new FolderHandle(i,this._cache)}if(t.create)return s[i]=!1,await this._cache.put(i,new Response("{}",DIR)),await this._save(s),new FolderHandle(i,this._cache);throw new DOMException(...GONE)}get _tree(){return this._cache.match(this._dir).then((e=>e.json())).catch((e=>{throw new DOMException(...GONE)}))}_save(e){return this._cache.put(this._dir,new Response(JSON.stringify(e),DIR))}async getFileHandle(e,t){const i=this._dir.endsWith("/")?this._dir+e:`${this._dir}/${e}`,s=await this._tree;if(hasOwn.call(s,i)){if(!s[i])throw new DOMException(...MISMATCH);return new FileHandle(i,this._cache)}if(t.create){const e=await this._tree;return e[i]=!0,await this._cache.put(i,new Response("",FILE())),await this._save(e),new FileHandle(i,this._cache)}throw new DOMException(...GONE)}async removeEntry(e,t){const i=await this._tree,s=this._dir.endsWith("/")?this._dir+e:`${this._dir}/${e}`;if(!hasOwn.call(i,s))throw new DOMException(...GONE);if(t.recursive){const e=[...Object.entries(i)];for(;e.length;){const[t,i]=e.pop();if(i)await this._cache.delete(t);else{const i=await this._cache.match(t).then((e=>e.json()));e.push(...Object.entries(i))}}delete i[s]}else{const e=i[s];if(delete i[s],e)await this._cache.delete(s);else{const e=await this._cache.match(s).then((e=>e.json()));if(Object.keys(e).length)throw new DOMException(...MOD_ERR);await this._cache.delete(s)}}await this._save(i)}}export default async function(){const e=await caches.open("sandboxed-fs");return await e.match("/")||await e.put("/",new Response("{}",DIR)),new FolderHandle(location.origin+"/",e)}