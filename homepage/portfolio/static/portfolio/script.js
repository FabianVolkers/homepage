var slideIndex = 1;
showDivs(slideIndex);

function plusDivs(n) {
  showDivs(slideIndex += n);
}

function currentDiv(n) {
  showDivs(slideIndex = n);
}

function showDivs(n) {
  var i;
  var x = document.getElementsByClassName("spotlight-img");

  if (x.length > 0) {
    var captions = document.getElementsByClassName("spotlight-caption");
    var dots = document.getElementsByClassName("spotlight-indicator");
    if (n > x.length) {
      slideIndex = 1
    }
    if (n < 1) {
      slideIndex = x.length
    }
    for (i = 0; i < x.length; i++) {
      x[i].style.display = "none";
      captions[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" indicator-white", "");
    }
    x[slideIndex - 1].style.display = "block";
    captions[slideIndex - 1].style.display = "block";
    dots[slideIndex - 1].className += " indicator-white";
  }

}

function setImageSize() {
  var images = [];
  var spotlights = document.getElementsByClassName('spotlight-img');
  for (let spotlight of spotlights) {
    images.push(spotlight);
  }


  var collectionItems = document.getElementsByClassName('collection-item');
  for (let collectionItem of collectionItems) {
    images.push(collectionItem.getElementsByTagName('img')[0])

  }
  const divRatio = 16 / 9;

  for (let image of images) {
    let width = image.naturalWidth;
    let height = image.naturalHeight;
    let ratio = width / height;

    if (ratio > divRatio) {
      image.style.height = '100%';
    } else {
      image.style.width = '100%'
    }
  }
}