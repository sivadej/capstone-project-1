function confirmDelete(item){
	switch (item) {
		case 'acct':
			return confirm('Are you sure you want to delete your account? You will lose all your saved watchlists. This cannot be undone.');
		case 'list':
			return confirm('Are you sure you want to delete this watchlist? This cannot be undone.');
		case 'movie':
			return confirm('Are you sure you want to remove this movie from your list?');
	}
}