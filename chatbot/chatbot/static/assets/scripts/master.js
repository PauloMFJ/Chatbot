/*! file: master.js */
// --- Page Preload ---
// Remove preload class on page load
$(window).on("load", function() {
	$('body').removeClass('preload');
});
