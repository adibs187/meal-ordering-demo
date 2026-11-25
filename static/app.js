const state={restaurants:[],items:[],restaurantId:null};
const $=id=>document.getElementById(id);
function setConnection(status){
  const box=$("serverStatus");
  box.classList.remove("connected","error");
  if(status==="connected"){box.classList.add("connected");$("serverText").textContent="מחובר ל־API ולמסד הנתונים"}
  else if(status==="error"){box.classList.add("error");$("serverText").textContent="אין חיבור למסד הנתונים"}
  else $("serverText").textContent="בודק חיבור...";
}
const api=async(url,options={})=>{
  let response;
  try{response=await fetch(url,{headers:{"Content-Type":"application/json"},...options})}
  catch(error){setConnection("error");throw new Error("אין חיבור לשרת")}
  const data=await response.json().catch(()=>({}));
  if(!response.ok){if(response.status===503)setConnection("error");throw new Error(data.detail||"הפעולה נכשלה")}
  return data;
};
function notify(message,error=false){const box=$("status");box.textContent=message;box.style.background=error?"#8d2929":"#153b2c";box.classList.add("show");setTimeout(()=>box.classList.remove("show"),2800)}
async function loadRestaurants(){
  state.restaurants=await api("/api/restaurants");
  setConnection("connected");
  $("restaurant").innerHTML=state.restaurants.map(r=>`<option value="${r.restaurant_id}">${escapeHtml(r.restaurant_name)}</option>`).join("");
  if(state.restaurants.length){state.restaurantId=Number($("restaurant").value);await loadItems()}
}
async function loadItems(){
  state.items=await api(`/api/menu-items?restaurant_id=${state.restaurantId}`);
  setConnection("connected");
  render();
}
function escapeHtml(value){const div=document.createElement("div");div.textContent=value??"";return div.innerHTML}
function render(){
  const q=$("search").value.trim().toLowerCase();
  const shown=state.items.filter(i=>(i.item_name+" "+i.description).toLowerCase().includes(q));
  $("totalCount").textContent=state.items.length;
  $("availableCount").textContent=state.items.filter(i=>i.in_stock).length;
  $("missingCount").textContent=state.items.filter(i=>!i.in_stock).length;
  $("emptyState").hidden=shown.length>0;
  $("menuGrid").innerHTML=shown.map(item=>`
    <article class="menu-card">
      <div class="card-meta"><h3>${escapeHtml(item.item_name)}</h3><button class="edit" data-edit="${item.item_id}">עריכה</button></div>
      <p>${escapeHtml(item.description)||"ללא תיאור"}</p>
      <div class="card-actions">
        <span class="price">₪${Number(item.price).toFixed(2)}</span>
        <button class="stock ${item.in_stock?"available":"missing"}" data-stock="${item.item_id}">
          ${item.in_stock?"זמינה":"חסרה"}
        </button>
      </div>
    </article>`).join("");
}
function openDialog(item=null){
  $("itemId").value=item?.item_id??"";
  $("itemName").value=item?.item_name??"";
  $("itemName").readOnly=Boolean(item);
  $("description").value=item?.description??"";
  $("price").value=item?.price??"";
  $("inStock").checked=item?.in_stock??true;
  $("inStock").disabled=Boolean(item);
  $("useCase").textContent=item?"UC025":"UC024";
  $("dialogTitle").textContent=item?"עריכת המחיר והתיאור":"הוספת מנה חדשה";
  $("nameError").textContent="";$("priceError").textContent="";
  $("dialogLayer").hidden=false;setTimeout(()=>$("itemName").focus(),30);
}
function closeDialog(){$("dialogLayer").hidden=true}
async function saveItem(event){
  event.preventDefault();
  const id=$("itemId").value;
  const name=$("itemName").value.trim(),price=Number($("price").value);
  $("nameError").textContent=!id&&name.length<2?"יש להזין לפחות שני תווים":"";
  $("priceError").textContent=price<=0?"המחיר חייב להיות גדול מאפס":"";
  if((!id&&name.length<2)||price<=0)return;
  const payload=id
    ? {description:$("description").value.trim(),price}
    : {restaurant_id:state.restaurantId,item_name:name,description:$("description").value.trim(),price,in_stock:$("inStock").checked};
  try{
    await api(id?`/api/menu-items/${id}`:"/api/menu-items",{method:id?"PUT":"POST",body:JSON.stringify(payload)});
    closeDialog();await loadItems();notify(id?"המנה עודכנה בהצלחה":"המנה נוספה בהצלחה");
  }catch(error){notify(error.message,true)}
}
async function toggleStock(id){
  const item=state.items.find(i=>i.item_id===id);if(!item)return;
  try{await api(`/api/menu-items/${id}/stock`,{method:"PATCH",body:JSON.stringify({in_stock:!item.in_stock})});await loadItems();notify("מצב הזמינות עודכן")}
  catch(error){notify(error.message,true)}
}
$("restaurant").addEventListener("change",async e=>{state.restaurantId=Number(e.target.value);try{await loadItems()}catch(error){notify(error.message,true)}});
$("search").addEventListener("input",render);
$("addButton").addEventListener("click",()=>openDialog());
$("refreshButton").addEventListener("click",()=>loadItems().catch(e=>notify(e.message,true)));
$("closeButton").addEventListener("click",closeDialog);$("cancelButton").addEventListener("click",closeDialog);$("backdrop").addEventListener("click",closeDialog);
$("itemForm").addEventListener("submit",saveItem);
$("menuGrid").addEventListener("click",e=>{const edit=e.target.closest("[data-edit]"),stock=e.target.closest("[data-stock]");if(edit)openDialog(state.items.find(i=>i.item_id===Number(edit.dataset.edit)));if(stock)toggleStock(Number(stock.dataset.stock))});
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeDialog()});
setConnection("checking");
loadRestaurants().catch(error=>{setConnection("error");notify(`${error.message}. יש לבדוק את חיבור SQL Server.`,true)});
