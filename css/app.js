let slideIndex = 1;
let numSlides = document.getElementsByClassName("slide").length;
let translateValue = (numSlides - 1) * -100;
showSlides(slideIndex);

// Next/previous controls
function changeSlide(n) {
  showSlides((slideIndex += n));
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides((slideIndex = n));
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("slide");
  let dots = document.getElementsByClassName("dot");
  let bgs = document.getElementsByClassName("slide-photo");
  if (n > slides.length) {
    slideIndex = 1;
  }
  if (n < 1) {
    slideIndex = slides.length;
  }

  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }

  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }

  translateValue = (slideIndex - 1) * -100;

  for (i = 0; i < bgs.length; i++) {
    bgs[i].style.translate = String(translateValue).concat("%");
  }

  slides[slideIndex - 1].style.display = "grid";
  dots[slideIndex - 1].className += " active";
}
