function sharefeature(zigurl){
	if(navigator.share){
		navigator.share({
			text: 'Check this out!',
			url: zigurl,
			title: "Jynx.in"
		})
	}else{
		navigator.clipboard.writeText(zigurl);
		UIkit.notification({message: '<span uk-icon=\'icon: star\'></span> Zig URL copied to clipboard'});
	}
}