;(function () {
  var lightbox = null
  var lightboxImage = null
  var lightboxCaption = null
  var closeButton = null
  var previousFocus = null

  function ensureLightbox() {
    if (lightbox) {
      return
    }

    lightbox = document.createElement('div')
    lightbox.className = 'ds-screenshot-lightbox'
    lightbox.setAttribute('role', 'dialog')
    lightbox.setAttribute('aria-modal', 'true')
    lightbox.setAttribute('aria-label', 'Просмотр скриншота')
    lightbox.setAttribute('aria-hidden', 'true')

    closeButton = document.createElement('button')
    closeButton.className = 'ds-screenshot-lightbox__close'
    closeButton.type = 'button'
    closeButton.setAttribute('aria-label', 'Закрыть просмотр')
    closeButton.textContent = '×'

    var figure = document.createElement('figure')
    figure.className = 'ds-screenshot-lightbox__figure'

    lightboxImage = document.createElement('img')
    lightboxImage.className = 'ds-screenshot-lightbox__image'
    lightboxImage.alt = ''

    lightboxCaption = document.createElement('figcaption')
    lightboxCaption.className = 'ds-screenshot-lightbox__caption'

    figure.appendChild(lightboxImage)
    figure.appendChild(lightboxCaption)
    lightbox.appendChild(closeButton)
    lightbox.appendChild(figure)
    document.body.appendChild(lightbox)

    closeButton.addEventListener('click', closeLightbox)
    lightbox.addEventListener('click', function (event) {
      if (event.target === lightbox) {
        closeLightbox()
      }
    })
  }

  function openLightbox(image) {
    ensureLightbox()

    previousFocus = document.activeElement
    var alt = image.getAttribute('alt') || 'Скриншот'

    lightboxImage.src = image.currentSrc || image.src
    lightboxImage.alt = alt
    lightboxCaption.textContent = alt
    lightbox.setAttribute('aria-hidden', 'false')
    lightbox.dataset.open = 'true'
    document.documentElement.classList.add('ds-screenshot-lightbox-open')
    closeButton.focus()
  }

  function closeLightbox() {
    if (!lightbox || lightbox.dataset.open !== 'true') {
      return
    }

    lightbox.setAttribute('aria-hidden', 'true')
    delete lightbox.dataset.open
    lightboxImage.removeAttribute('src')
    document.documentElement.classList.remove('ds-screenshot-lightbox-open')

    if (previousFocus && typeof previousFocus.focus === 'function') {
      previousFocus.focus()
    }
  }

  function handleScreenshotKeydown(event) {
    if (event.key !== 'Enter' && event.key !== ' ') {
      return
    }

    event.preventDefault()
    openLightbox(event.currentTarget)
  }

  function enhanceScreenshots() {
    var screenshots = document.querySelectorAll('.ds-screenshot:not([data-lightbox-ready])')

    screenshots.forEach(function (image) {
      image.dataset.lightboxReady = 'true'
      image.tabIndex = 0
      image.setAttribute('role', 'button')
      image.setAttribute(
        'aria-label',
        'Открыть скриншот: ' + (image.getAttribute('alt') || 'изображение')
      )
      image.title = 'Открыть скриншот'
      image.addEventListener('click', function () {
        openLightbox(image)
      })
      image.addEventListener('keydown', handleScreenshotKeydown)
    })
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      closeLightbox()
      return
    }

    if (event.key === 'Tab' && lightbox && lightbox.dataset.open === 'true') {
      event.preventDefault()
      closeButton.focus()
    }
  })

  if (window.document$ && typeof window.document$.subscribe === 'function') {
    window.document$.subscribe(enhanceScreenshots)
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceScreenshots)
  } else {
    enhanceScreenshots()
  }
})()
