// Конфигуратор ПК
document.addEventListener('DOMContentLoaded', function() {
    // База данных компонентов
    const components = {
        cpus: [
            { id: 1, name: 'Intel Core i5-12400F', price: 15000, socket: 'LGA1700', tdp: 65 },
            { id: 2, name: 'AMD Ryzen 5 5600X', price: 18000, socket: 'AM4', tdp: 65 },
            { id: 3, name: 'Intel Core i7-12700K', price: 25000, socket: 'LGA1700', tdp: 125 },
            { id: 4, name: 'AMD Ryzen 7 5800X', price: 22000, socket: 'AM4', tdp: 105 }
        ],
        motherboards: [
            { id: 1, name: 'ASUS PRIME B660-PLUS', price: 12000, socket: 'LGA1700', ramType: 'DDR4' },
            { id: 2, name: 'MSI B550-A PRO', price: 11000, socket: 'AM4', ramType: 'DDR4' },
            { id: 3, name: 'Gigabyte Z690 UD', price: 15000, socket: 'LGA1700', ramType: 'DDR4' },
            { id: 4, name: 'ASUS ROG STRIX X570-E', price: 20000, socket: 'AM4', ramType: 'DDR4' }
        ],
        gpus: [
            { id: 1, name: 'NVIDIA GeForce RTX 3060', price: 35000, power: 170 },
            { id: 2, name: 'AMD Radeon RX 6600', price: 30000, power: 132 },
            { id: 3, name: 'NVIDIA GeForce RTX 3070', price: 50000, power: 220 },
            { id: 4, name: 'AMD Radeon RX 6700 XT', price: 45000, power: 230 }
        ],
        rams: [
            { id: 1, name: 'Corsair Vengeance LPX 16GB', price: 6000, type: 'DDR4' },
            { id: 2, name: 'Kingston Fury Beast 32GB', price: 10000, type: 'DDR4' },
            { id: 3, name: 'G.Skill Trident Z RGB 16GB', price: 8000, type: 'DDR4' },
            { id: 4, name: 'Crucial Ballistix 32GB', price: 12000, type: 'DDR4' }
        ],
        storages: [
            { id: 1, name: 'Samsung 970 EVO Plus 500GB', price: 7000, type: 'NVMe' },
            { id: 2, name: 'WD Blue 1TB HDD', price: 3000, type: 'SATA' },
            { id: 3, name: 'Crucial P5 1TB', price: 10000, type: 'NVMe' },
            { id: 4, name: 'Seagate BarraCuda 2TB', price: 5000, type: 'SATA' }
        ],
        psus: [
            { id: 1, name: 'Corsair RM650x', price: 8000, wattage: 650 },
            { id: 2, name: 'Be Quiet! Pure Power 11 700W', price: 8500, wattage: 700 },
            { id: 3, name: 'Seasonic Focus GX-750', price: 10000, wattage: 750 },
            { id: 4, name: 'EVGA SuperNOVA 850 G6', price: 12000, wattage: 850 }
        ],
        cases: [
            { id: 1, name: 'NZXT H510', price: 7000, formFactor: 'ATX' },
            { id: 2, name: 'Fractal Design Meshify C', price: 8000, formFactor: 'ATX' },
            { id: 3, name: 'Cooler Master MasterBox Q300L', price: 5000, formFactor: 'mATX' },
            { id: 4, name: 'Lian Li PC-O11 Dynamic', price: 12000, formFactor: 'ATX' }
        ]
    };

    // Заполняем выпадающие списки
    fillDropdown('cpu-select', components.cpus);
    fillDropdown('motherboard-select', components.motherboards);
    fillDropdown('gpu-select', components.gpus);
    fillDropdown('ram-select', components.rams);
    fillDropdown('storage-select', components.storages);
    fillDropdown('psu-select', components.psus);
    fillDropdown('case-select', components.cases);

    // Обработчики изменений
    document.querySelectorAll('.component-dropdown').forEach(select => {
        select.addEventListener('change', updateBuildSummary);
    });

    // Кнопка сохранения сборки
    document.getElementById('save-build').addEventListener('click', saveBuild);

    // Загрузка сохраненной сборки, если есть
    loadSavedBuild();

    function fillDropdown(id, items) {
        const select = document.getElementById(id);
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = `${item.name} - ${item.price} ₽`;
            select.appendChild(option);
        });
    }

    function updateBuildSummary() {
        const selectedComponents = {};
        let totalPrice = 0;
        let hasSelection = false;

        // Собираем выбранные компоненты
        document.querySelectorAll('.component-dropdown').forEach(select => {
            const category = select.id.replace('-select', '');
            const selectedId = parseInt(select.value);
            
            if (selectedId) {
                hasSelection = true;
                const component = components[category + 's'].find(c => c.id === selectedId);
                selectedComponents[category] = component;
                totalPrice += component.price;
            } else {
                selectedComponents[category] = null;
            }
        });

        // Обновляем список компонентов
        const componentsList = document.getElementById('selected-components');
        componentsList.innerHTML = '';
        
        for (const [category, component] of Object.entries(selectedComponents)) {
            if (component) {
                const item = document.createElement('div');
                item.className = 'component-item';
                item.innerHTML = `
                    <span class="component-name">${component.name}</span>
                    <span class="component-price">${component.price} ₽</span>
                `;
                componentsList.appendChild(item);
            }
        }

        // Обновляем общую цену
        document.getElementById('total-price').textContent = totalPrice;

        // Проверяем совместимость
        checkCompatibility(selectedComponents);
    }

    function checkCompatibility(components) {
        const errorsContainer = document.getElementById('compatibility-errors');
        errorsContainer.innerHTML = '';
        const errors = [];

        // Проверка совместимости процессора и материнской платы
        if (components.cpu && components.motherboard) {
            if (components.cpu.socket !== components.motherboard.socket) {
                errors.push('Процессор и материнская плата не совместимы по сокету');
            }
        }

        // Проверка совместимости ОЗУ и материнской платы
        if (components.ram && components.motherboard) {
            if (components.ram.type !== components.motherboard.ramType) {
                errors.push('Тип оперативной памяти не совместим с материнской платой');
            }
        }

        // Проверка мощности блока питания
        if (components.psu) {
            let totalPower = 0;
            if (components.cpu) totalPower += components.cpu.tdp;
            if (components.gpu) totalPower += components.gpu.power;
            // Добавляем 100W для остальных компонентов
            totalPower += 100;
            
            if (totalPower > components.psu.wattage * 0.8) { // Используем 80% от номинала БП
                errors.push(`Блок питания может быть недостаточно мощным (рекомендуется от ${Math.ceil(totalPower / 0.8)}W)`);
            }
        }

        // Проверка совместимости корпуса и материнской платы
        if (components.case && components.motherboard) {
            const caseFormFactor = components.case.formFactor;
            const mbFormFactor = components.motherboard.formFactor || 'ATX'; // По умолчанию ATX
            
            // Упрощенная проверка совместимости форм-факторов
            if (caseFormFactor === 'mATX' && mbFormFactor === 'ATX') {
                errors.push('Материнская плата ATX не поместится в корпус mATX');
            }
        }

        // Выводим ошибки
        if (errors.length > 0) {
            errors.forEach(error => {
                const errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                errorElement.textContent = error;
                errorsContainer.appendChild(errorElement);
            });
        }
    }

    function saveBuild() {
        const build = {};
        document.querySelectorAll('.component-dropdown').forEach(select => {
            const category = select.id.replace('-select', '');
            build[category] = select.value;
        });
        
        localStorage.setItem('savedPcBuild', JSON.stringify(build));
        alert('Сборка сохранена!');
    }

    function loadSavedBuild() {
        const savedBuild = localStorage.getItem('savedPcBuild');
        if (savedBuild) {
            const build = JSON.parse(savedBuild);
            for (const [category, id] of Object.entries(build)) {
                const select = document.getElementById(`${category}-select`);
                if (select && id) {
                    select.value = id;
                }
            }
            updateBuildSummary();
        }
    }

    // Карта магазинов
    // Данные магазинов
    const stores = [
        {
            id: 1,
            name: 'Центральный магазин',
            address: 'ул. Компьютерная, 1',
            coords: [53.379231, 58.976412], // Москва
            deliveryZones: [
                { radius: 5, price: 0 },
                { radius: 10, price: 500 },
                { radius: 20, price: 1000 },
                { radius: Infinity, price: 2000 }
            ]
        },
        {
            id: 2,
            name: 'Северный филиал',
            address: 'пр. Процессорный, 15',
            coords: [53.367364, 58.989356], // Север Москвы
            deliveryZones: [
                { radius: 5, price: 0 },
                { radius: 15, price: 700 },
                { radius: 30, price: 1500 },
                { radius: Infinity, price: 2500 }
            ]
        },
        {
            id: 3,
            name: 'Южный пункт выдачи',
            address: 'бул. Видеокартный, 42',
            coords: [53.359246, 58.960902], // Юг Москвы
            deliveryZones: [
                { radius: 3, price: 0 },
                { radius: 10, price: 600 },
                { radius: 20, price: 1200 },
                { radius: Infinity, price: 2200 }
            ]
        }
    ];

    // Инициализация карты
    const map = L.map('map').setView([53.403807, 58.975614], 11);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Добавляем маркеры магазинов
    stores.forEach(store => {
        const marker = L.marker(store.coords).addTo(map)
            .bindPopup(`<b>${store.name}</b><br>${store.address}`);
        
        marker.on('click', function() {
            document.getElementById('store-select').value = store.id;
            updateDeliveryInfo();
        });
    });

    // Заполняем выпадающий список магазинов
    const storeSelect = document.getElementById('store-select');
    stores.forEach(store => {
        const option = document.createElement('option');
        option.value = store.id;
        option.textContent = `${store.name} - ${store.address}`;
        storeSelect.appendChild(option);
    });

    // Обработчики событий
    storeSelect.addEventListener('change', updateDeliveryInfo);
    document.querySelectorAll('input[name="delivery"]').forEach(radio => {
        radio.addEventListener('change', updateDeliveryInfo);
    });

    function updateDeliveryInfo() {
        const storeId = parseInt(storeSelect.value);
        const deliveryType = document.querySelector('input[name="delivery"]:checked').value;
        const detailsContainer = document.getElementById('delivery-details');
        
        if (!storeId) {
            detailsContainer.innerHTML = '<p>Выберите магазин для расчета стоимости доставки</p>';
            return;
        }
        
        const store = stores.find(s => s.id === storeId);
        
        if (deliveryType === 'pickup') {
            detailsContainer.innerHTML = `
                <h4>Самовывоз</h4>
                <p><strong>Адрес:</strong> ${store.address}</p>
                <p><strong>Стоимость:</strong> Бесплатно</p>
                <p>Часы работы: 10:00 - 20:00</p>
            `;
        } else {
            detailsContainer.innerHTML = `
                <h4>Доставка</h4>
                <p><strong>Адрес магазина:</strong> ${store.address}</p>
                <div class="delivery-zones">
                    <p><strong>Зоны доставки:</strong></p>
                    <ul>
                        ${store.deliveryZones.map(zone => `
                            <li>До ${zone.radius} км - ${zone.price} ₽</li>
                        `).join('')}
                    </ul>
                </div>
                <div class="address-input">
                    <label for="delivery-address">Введите ваш адрес:</label>
                    <input type="text" id="delivery-address" placeholder="ул. Примерная, 10">
                    <button id="calculate-delivery" class="calculate-btn">Рассчитать стоимость</button>
                </div>
                <div id="delivery-result"></div>
            `;
            
            document.getElementById('calculate-delivery').addEventListener('click', calculateDelivery);
        }
    }

    function calculateDelivery() {
        const address = document.getElementById('delivery-address').value;
        if (!address) {
            alert('Введите адрес для расчета доставки');
            return;
        }
        
        // Здесь должна быть реальная геокодировка адреса, но для примера используем случайное расстояние
        const storeId = parseInt(storeSelect.value);
        const store = stores.find(s => s.id === storeId);
        const distance = Math.random() * 30; // Случайное расстояние до 30 км
        
        let deliveryPrice = 0;
        for (const zone of store.deliveryZones) {
            if (distance <= zone.radius) {
                deliveryPrice = zone.price;
                break;
            }
        }
        
        document.getElementById('delivery-result').innerHTML = `
            <p><strong>Расчет доставки:</strong></p>
            <p>Расстояние до магазина: ${distance.toFixed(1)} км</p>
            <p><strong>Стоимость доставки:</strong> ${deliveryPrice} ₽</p>
        `;
    }
});