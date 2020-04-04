let movieWatchlistObj = {};
const btns = document.querySelectorAll('.add-to-list-btn');
btns.forEach(btn=>{
	btn.addEventListener('click',e=>{
		e.preventDefault();
		movieWatchlistObj = {
			nfid : e.target.dataset.nfid,
			title : e.target.dataset.title,
			vtype : e.target.dataset.vtype,
		}
		getWatchlistSelector();
	})
})

async function getWatchlistSelector(){
	renderHtmlToModal('','main-modal-message');
	try {
		response = await axios.get('/pick_watchlist_from_search');
		renderHtmlToModal(response.data, 'main-modal-body');
	} catch {
		renderHtmlToModal('an error occurred', 'main-modal-body');
	}
	watchlistSelectBtn = document.getElementById('submit-watchlist-pick');
	watchlistSelectBtn.addEventListener('click',async e=>{
		e.preventDefault();
		const watchlistDropdown = document.getElementById('watchlist');
		movieWatchlistObj.watchlistId = watchlistDropdown.value;
		try {
			resp = await axios.post('/watchlist_add_from_search', movieWatchlistObj);
			if (resp.status === 200) {
				renderHtmlToModal('','main-modal-body');
				renderHtmlToModal(resp.data,'main-modal-message');
			}
			else if (resp.status === 202)
				renderHtmlToModal(resp.data,'main-modal-message');
			else {
				throw "unrecognized response";
			}
		} catch {
			appendHtmlToModal('error','main-modal-body')
		}
	})
}

function renderHtmlToModal(resp, targetId){
	document.getElementById(targetId).innerHTML = resp;
}
function appendHtmlToModal(resp, targetId){
	document.getElementById(targetId).append(resp);
}