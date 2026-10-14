document.documentElement.classList.add('js');
const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('.nav');
toggle?.addEventListener('click',()=>{
  const open=toggle.getAttribute('aria-expanded')!=='true';
  toggle.setAttribute('aria-expanded',String(open));
  nav.classList.toggle('is-open',open);
  toggle.textContent=open?'Close':'Menu';
});
let authorshipFilter='all';
let publicationStatusFilter='all';
function filterPublications(){
  let count=0;
  document.querySelectorAll('.publication').forEach(p=>{
    p.hidden=(authorshipFilter!=='all'&&p.dataset.group!==authorshipFilter)||(publicationStatusFilter!=='all'&&p.dataset.status!==publicationStatusFilter);
    if(!p.hidden) count++;
  });
  document.querySelectorAll('.pub-group').forEach(section=>section.hidden=![...section.querySelectorAll('.publication')].some(p=>!p.hidden));
  document.querySelector('.result-count').textContent=`Showing ${count} ${count===1?'entry':'entries'}`;
}
document.querySelectorAll('.filter[data-filter]').forEach(button=>button.addEventListener('click',()=>{
  authorshipFilter=button.dataset.filter;
  document.querySelectorAll('.filter[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  filterPublications();
}));
document.querySelectorAll('.status-filter').forEach(button=>button.addEventListener('click',()=>{
  publicationStatusFilter=button.dataset.statusFilter;
  document.querySelectorAll('.status-filter').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  filterPublications();
}));
const dialog=document.querySelector('.citation-dialog');
let activeCitation='';
document.querySelectorAll('.cite-button').forEach(button=>button.addEventListener('click',()=>{
  activeCitation=button.dataset.citation;
  dialog.querySelector('pre').textContent=activeCitation;
  dialog.querySelector('.copy-status').textContent='';
  dialog.showModal();
}));
dialog?.querySelector('.close-dialog').addEventListener('click',()=>dialog.close());
dialog?.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}});
dialog?.querySelector('.copy-citation').addEventListener('click',async()=>{
  const status=dialog.querySelector('.copy-status');
  try{await navigator.clipboard.writeText(activeCitation);status.textContent='BibTeX copied.';}
  catch{status.textContent='Select the BibTeX above to copy it.';}
});
