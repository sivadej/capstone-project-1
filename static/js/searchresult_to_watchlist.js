console.log('search result to watchlist init');
const btns = document.querySelectorAll('.add-to-list-btn');
btns.forEach(btn=>{
	btn.addEventListener('click',e=>{
		e.preventDefault();
		getWatchlistSelector();
	})
})

async function getWatchlistSelector(){
try {
	response = await axios.get('/pick');
	renderHtmlToModal(response.data, 'main-modal-body');
} catch {
	renderHtmlToModal('an error occurred', 'main-modal-body');
}
}

function renderHtmlToModal(resp, targetId){
	document.getElementById(targetId).innerHTML = resp;
}