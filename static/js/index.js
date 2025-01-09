/*
index.js
Этот файл отвечает за создание и анимацию сетевой визуализации на странице. Использует HTML5 Canvas для отрисовки частиц и линий между ними.

Основные компоненты:
1. Класс `Particle`: Определяет свойства и поведение каждой частицы.
2. Функция `initParticles()`: Инициализирует массив частиц.
3. Функция `connectParticles()`: Соединяет близкие частицы линиями.
4. Функция `animate()`: Анимация движения частиц и обновление отрисовки.
5. Обработчик `resize`: Обновляет размеры Canvas при изменении окна.
*/

// Инициализация Canvas
const canvas = document.getElementById('network-canvas');
const ctx = canvas.getContext('2d');

// Устанавливаем размеры Canvas в соответствии с размером окна
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = []; // Массив частиц
const maxParticles = 100; // Максимальное количество частиц

// Класс, описывающий частицу
class Particle {
    constructor(x, y) {
        this.x = x; // Координата X
        this.y = y; // Координата Y
        this.vx = (Math.random() - 0.5) * 2; // Скорость по X
        this.vy = (Math.random() - 0.5) * 2; // Скорость по Y
        this.radius = Math.random() * 2 + 1; // Радиус частицы
    }

    // Отрисовка частицы
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'white'; // Цвет частицы
        ctx.fill();
    }

    // Обновление позиции частицы
    update() {
        this.x += this.vx;
        this.y += this.vy;

        // Отражение от границ Canvas
        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
    }
}

// Инициализация частиц
function initParticles() {
    particles = [];
    for (let i = 0; i < maxParticles; i++) {
        particles.push(new Particle(Math.random() * canvas.width, Math.random() * canvas.height));
    }
}

// Соединение близких частиц линиями
function connectParticles() {
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dist = Math.hypot(particles[i].x - particles[j].x, particles[i].y - particles[j].y); // Расстояние между частицами
            if (dist < 100) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'; // Полупрозрачный белый цвет линий
                ctx.lineWidth = 1; // Толщина линии
                ctx.stroke();
            }
        }
    }
}

// Анимация частиц
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Очистка Canvas
    particles.forEach(p => {
        p.update(); // Обновление положения частицы
        p.draw(); // Отрисовка частицы
    });
    connectParticles(); // Соединение частиц линиями
    requestAnimationFrame(animate); // Запрос следующего кадра
}

// Обновление размеров Canvas при изменении размера окна
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    initParticles(); // Переинициализация частиц
});

// Инициализация и запуск анимации
initParticles();
animate();
