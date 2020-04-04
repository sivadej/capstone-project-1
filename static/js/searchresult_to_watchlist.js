console.log('search result to watchlist init');
const btns = document.querySelectorAll('.add-to-list-btn');


let movieWatchlistObj = {};
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
	console.log(watchlistSelectBtn);
	watchlistSelectBtn.addEventListener('click',async e=>{
		e.preventDefault();
		const watchlistDropdown = document.getElementById('watchlist');
		movieWatchlistObj.watchlistId = watchlistDropdown.value;
		console.log(movieWatchlistObj.watchlistId);
		try {
			resp = await axios.post('/watchlist_add_from_search', movieWatchlistObj);
			console.log(resp)
			if (resp.status === 200)
				renderHtmlToModal(resp.data,'main-modal-body')
			else if (resp.status === 202)
				renderHtmlToModal(resp.data,'main-modal-message')
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