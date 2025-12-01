document.addEventListener('DOMContentLoaded', () => {
  const sliderConfigs = [
    { rangeId: 'range', valueId: 'value', progressId: 'progress_range' },
    { rangeId: 'range_2', valueId: 'value_2', progressId: 'progress_range_2' },
    { rangeId: 'range_3', valueId: 'value_3', progressId: 'progress_range_3' },
    { rangeId: 'range_4', valueId: 'value_4', progressId: 'progress_range_4' }
  ];

  const updateBubble = (rangeEl, valueEl, progressEl) => {
    if (!rangeEl || !valueEl) {
      return;
    }
    valueEl.textContent = rangeEl.value;
    const max = Number(rangeEl.max || 0);
    const current = Number(rangeEl.value || 0);
    const min = Number(rangeEl.min || 0);
    const range = max - min;
    const percentage = range > 0 ? ((current - min) / range) * 100 : 0;
    
    // Получаем ширину слайдера и размеры элементов
    const sliderWidth = rangeEl.offsetWidth || rangeEl.clientWidth;
    const thumbSize = 24; // Размер thumb слайдера
    const bubbleWidth = valueEl.offsetWidth || 50;
    
    // Вычисляем позицию центра thumb
    // Thumb центрируется на позиции, соответствующей проценту
    const thumbCenterPosition = (sliderWidth * percentage) / 100;
    
    // Центрируем bubble относительно центра thumb
    // transform: translateX(-50%) уже применяется в CSS, поэтому просто указываем позицию центра
    valueEl.style.left = `${thumbCenterPosition}px`;
    
    // Обновляем прогресс-бар
    if (progressEl) {
      progressEl.style.width = `${percentage}%`;
    }
  };

  sliderConfigs.forEach(({ rangeId, valueId, progressId }) => {
    const rangeEl = document.getElementById(rangeId);
    const valueEl = document.getElementById(valueId);
    const progressEl = document.getElementById(progressId);
    if (!rangeEl || !valueEl) {
      return;
    }
    
    // Обновляем при изменении слайдера
    rangeEl.addEventListener('input', () => updateBubble(rangeEl, valueEl, progressEl));
    
    // Обновляем при изменении размера окна
    window.addEventListener('resize', () => updateBubble(rangeEl, valueEl, progressEl));
    
    // Инициализация с небольшой задержкой для правильного вычисления размеров
    setTimeout(() => {
      updateBubble(rangeEl, valueEl, progressEl);
    }, 10);
  });

  const form = document.getElementById('reviewForm');
  form?.addEventListener('submit', () => {
    sliderConfigs.forEach(({ rangeId, valueId, progressId }) => {
      const rangeEl = document.getElementById(rangeId);
      const valueEl = document.getElementById(valueId);
      const progressEl = document.getElementById(progressId);
      updateBubble(rangeEl, valueEl, progressEl);
    });
  });
});