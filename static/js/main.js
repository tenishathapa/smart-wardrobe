document.addEventListener('DOMContentLoaded', function () {
  var AudioCtx = window.AudioContext || window.webkitAudioContext;
  var audioCtx = null;

  function playTone(freq, duration, type) {
    try {
      if (!audioCtx) {
        audioCtx = new AudioCtx();
      }
      var osc = audioCtx.createOscillator();
      var gain = audioCtx.createGain();
      osc.type = type || 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {}
  }

  function playClick() { playTone(800, 0.08, 'sine'); }
  function playSuccess() { playTone(523, 0.1, 'sine'); setTimeout(function () { playTone(659, 0.1, 'sine'); }, 100); setTimeout(function () { playTone(784, 0.15, 'sine'); }, 200); }
  function playHover() { playTone(600, 0.04, 'sine'); }

  var soundEnabled = localStorage.getItem('soundEnabled') !== 'false';

  document.addEventListener('click', function (e) {
    if (!soundEnabled) return;
    var tag = e.target.tagName;
    if (tag === 'BUTTON' || tag === 'A' || e.target.closest('button') || e.target.closest('a')) {
      playClick();
    }
  });

  document.querySelectorAll('.btn-primary, .btn-success').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (btn.type !== 'submit') return;
      playSuccess();
    });
  });

  var soundToggle = document.getElementById('soundToggle');
  if (soundToggle) {
    var icon = soundToggle.querySelector('i');
    if (!soundEnabled) {
      icon.className = 'bi bi-volume-mute-fill';
    }
    soundToggle.addEventListener('click', function () {
      soundEnabled = !soundEnabled;
      localStorage.setItem('soundEnabled', soundEnabled);
      icon.className = soundEnabled ? 'bi bi-volume-up-fill' : 'bi bi-volume-mute-fill';
    });
  }

  var themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      if (isDark) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        themeToggle.querySelector('i').className = 'bi bi-moon-fill';
      } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        themeToggle.querySelector('i').className = 'bi bi-sun-fill';
      }
    });
  }

  var savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    if (themeToggle) themeToggle.querySelector('i').className = 'bi bi-sun-fill';
  }

  var imageInput = document.getElementById('imageInput');
  var imagePreview = document.getElementById('imagePreview');
  if (imageInput && imagePreview) {
    imageInput.addEventListener('change', function (e) {
      var file = e.target.files[0];
      if (file) {
        var reader = new FileReader();
        reader.onload = function (e) {
          imagePreview.src = e.target.result;
          imagePreview.classList.add('show');
        };
        reader.readAsDataURL(file);
      } else {
        imagePreview.classList.remove('show');
      }
    });
  }

  var loadingOverlay = document.getElementById('loadingOverlay');
  if (loadingOverlay) {
    document.querySelectorAll('form').forEach(function (form) {
      form.addEventListener('submit', function () {
        loadingOverlay.classList.add('active');
      });
    });
  }

  var scrollAnims = document.querySelectorAll('.animate-on-scroll');
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-fadeIn');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  scrollAnims.forEach(function (el) { observer.observe(el); });
});
