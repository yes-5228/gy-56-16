<template>
  <section class="page-stack">
    <div class="metrics-row">
      <MetricCard label="线路数量" :value="routes.length" hint="覆盖多目的地线路" />
      <MetricCard label="成团中" :value="formingCount" hint="持续收客线路" />
      <MetricCard label="平均预算" :value="averageBudget" hint="按线路预计总价" />
    </div>
    <div class="route-grid">
      <RouteCard
        v-for="route in routes"
        :key="route.id"
        :route="route"
        :priceCalendar="priceCalendar"
        @view-detail="openDetail"
      />
    </div>

    <div v-if="selectedRoute" class="modal-overlay" @click.self="selectedRoute = null">
      <div class="modal-content">
        <div class="modal-head">
          <div>
            <p class="eyebrow">{{ selectedRoute.city }} · {{ selectedRoute.days }} 天</p>
            <h3>{{ selectedRoute.title }}</h3>
          </div>
          <button type="button" class="close-btn" @click="selectedRoute = null">×</button>
        </div>
        <p class="description">{{ selectedRoute.description }}</p>

        <div v-if="selectedCalendar.length" class="detail-section">
          <p class="eyebrow">价格日历 · 选择出行日期</p>
          <div class="calendar-grid">
            <button
              v-for="item in selectedCalendar"
              :key="item.id"
              type="button"
              :class="{ active: selectedDateId === item.id, expired: isExpired(item) }"
              :disabled="isExpired(item)"
              @click="selectDate(item)"
            >
              <div class="cal-date">
                <strong>{{ getDayOfWeek(item.travel_date) }}</strong>
                <span>{{ formatDate(item.travel_date) }}</span>
              </div>
              <div class="cal-price">
                <em>¥{{ item.base_cost }}</em>
                <span>基础费</span>
              </div>
              <div class="cal-stock">
                <span v-if="isExpired(item)" class="expired-tag">已截止</span>
                <span v-else-if="item.remaining_inventory <= 0" class="full-tag">名额已满</span>
                <span v-else class="stock-tag">剩余 {{ item.remaining_inventory }} 位</span>
              </div>
              <div v-if="item.registration_deadline" class="cal-deadline">
                截止: {{ formatDateTime(item.registration_deadline) }}
              </div>
            </button>
          </div>
        </div>
        <div v-else class="detail-section empty-calendar">
          <p class="eyebrow">价格日历</p>
          <p>暂无价格日历，使用线路统一价格</p>
        </div>

        <div class="detail-section price-summary">
          <p class="eyebrow">费用明细</p>
          <div class="budget-grid">
            <span>基础费用 <b>¥{{ currentPricing.base_cost }}</b></span>
            <span>导游服务 <b>¥{{ selectedRoute.guide_fee }}</b></span>
            <span>门票合计 <b>¥{{ selectedRoute.ticket_total }}</b></span>
          </div>
          <div class="total-row">
            <span>预计总价</span>
            <strong>¥{{ currentPricing.estimated_cost }}</strong>
          </div>
          <div v-if="selectedDateStock !== null" class="stock-row">
            <span>当前选择日期可报名</span>
            <strong>{{ selectedDateStock }} 位</strong>
          </div>
        </div>

        <div class="detail-section">
          <p class="eyebrow">行程安排</p>
          <ol class="stop-list">
            <li v-for="stop in selectedRoute.stops" :key="stop.id">
              <span>D{{ stop.day }}-{{ stop.order }}</span>
              <div>
                <b>{{ stop.attraction.name }}</b>
                <p>{{ stop.note }}</p>
              </div>
            </li>
          </ol>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import MetricCard from "../components/MetricCard.vue";
import RouteCard from "../components/RouteCard.vue";

const props = defineProps({
  routes: { type: Array, required: true },
  priceCalendar: { type: Array, default: () => [] },
});

const selectedRoute = ref(null);
const selectedDateMap = reactive({});

const selectedDateId = computed(() => {
  if (!selectedRoute.value) return null;
  return selectedDateMap[selectedRoute.value.id] || null;
});

const formingCount = computed(() => props.routes.filter((route) => route.status === "forming").length);
const averageBudget = computed(() => {
  if (!props.routes.length) return "¥0";
  const total = props.routes.reduce((sum, route) => sum + Number(route.estimated_cost), 0);
  return `¥${Math.round(total / props.routes.length)}`;
});

const selectedCalendar = computed(() => {
  if (!selectedRoute.value) return [];
  const routeId = selectedRoute.value.id;
  return props.priceCalendar
    .filter((item) => item.route === routeId || item.route_id === routeId)
    .sort((a, b) => new Date(a.travel_date) - new Date(b.travel_date));
});

const currentPricing = computed(() => {
  if (!selectedRoute.value) return { base_cost: "0", estimated_cost: "0" };
  const selected = selectedCalendar.value.find((item) => item.id === selectedDateId.value);
  if (selected) {
    const base = Number(selected.base_cost);
    const guide = Number(selectedRoute.value.guide_fee);
    const ticket = Number(selectedRoute.value.ticket_total);
    return {
      base_cost: selected.base_cost,
      estimated_cost: (base + guide + ticket).toFixed(2),
    };
  }
  return {
    base_cost: selectedRoute.value.base_cost,
    estimated_cost: selectedRoute.value.estimated_cost,
  };
});

const selectedDateDeadline = computed(() => {
  const selected = selectedCalendar.value.find((item) => item.id === selectedDateId.value);
  if (!selected) return null;
  return selected.registration_deadline;
});

const selectedDateStock = computed(() => {
  const selected = selectedCalendar.value.find((item) => item.id === selectedDateId.value);
  if (!selected) return null;
  return selected.remaining_inventory;
});

function openDetail(route) {
  selectedRoute.value = route;
  const savedId = selectedDateMap[route.id];
  const savedItem = selectedCalendar.value.find((item) => item.id === savedId);
  if (savedItem && !isExpired(savedItem) && savedItem.remaining_inventory > 0) {
    return;
  }
  const firstAvailable = selectedCalendar.value.find(
    (item) => !isExpired(item) && item.remaining_inventory > 0
  );
  if (firstAvailable) {
    selectedDateMap[route.id] = firstAvailable.id;
  }
}

function selectDate(item) {
  if (!isExpired(item) && item.remaining_inventory > 0) {
    if (selectedRoute.value) {
      selectedDateMap[selectedRoute.value.id] = item.id;
    }
  }
}

function isExpired(item) {
  if (!item.registration_deadline) return false;
  return new Date(item.registration_deadline) < new Date();
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${month}-${day}`;
}

function formatDateTime(dateStr) {
  const d = new Date(dateStr);
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hour = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${month}-${day} ${hour}:${min}`;
}

function getDayOfWeek(dateStr) {
  const days = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
  const d = new Date(dateStr);
  return days[d.getDay()];
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: grid;
  place-items: center;
  z-index: 100;
  padding: 24px;
}
.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 720px;
  width: 100%;
  max-height: 90vh;
  overflow: auto;
  padding: 28px;
  display: grid;
  gap: 20px;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}
.modal-head h3 {
  margin: 4px 0 0;
}
.close-btn {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 8px;
  background: #f1f5f9;
  font-size: 22px;
  cursor: pointer;
  color: #475569;
}
.close-btn:hover {
  background: #e2e8f0;
}
.description {
  margin: 0;
  color: #65717f;
}
.detail-section {
  display: grid;
  gap: 10px;
}
.detail-section.empty-calendar p {
  margin: 0;
  color: #94a3b8;
}
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}
.calendar-grid button {
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  background: white;
  text-align: left;
  display: grid;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.calendar-grid button:hover:not(:disabled) {
  border-color: #0f766e;
  box-shadow: 0 4px 12px rgba(15, 118, 110, 0.15);
}
.calendar-grid button.active {
  border-color: #0f766e;
  background: #f0fdfa;
}
.calendar-grid button.expired {
  opacity: 0.5;
  cursor: not-allowed;
  background: #fef2f2;
}
.cal-date {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.cal-date strong {
  font-size: 14px;
  color: #17202a;
}
.cal-date span {
  font-size: 13px;
  color: #65717f;
  font-weight: 600;
}
.cal-price em {
  font-style: normal;
  font-size: 22px;
  font-weight: 700;
  color: #0f766e;
}
.cal-price span {
  font-size: 12px;
  color: #65717f;
  margin-left: 4px;
}
.cal-stock .stock-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  background: #dcfce7;
  color: #166534;
  font-size: 12px;
  font-weight: 600;
}
.cal-stock .expired-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  background: #fee2e2;
  color: #991b1b;
  font-size: 12px;
  font-weight: 600;
}
.cal-stock .full-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  background: #fef3c7;
  color: #92400e;
  font-size: 12px;
  font-weight: 600;
}
.cal-deadline {
  font-size: 11px;
  color: #94a3b8;
}
.price-summary {
  background: #f8fafc;
  border-radius: 10px;
  padding: 16px;
}
.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #cbd5e1;
}
.total-row span {
  color: #475569;
  font-weight: 600;
}
.total-row strong {
  font-size: 24px;
  color: #0f766e;
}
.stock-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.stock-row span {
  color: #64748b;
  font-size: 14px;
}
.stock-row strong {
  color: #0369a1;
  font-size: 18px;
}
.stop-list {
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
  list-style: none;
}
.stop-list li {
  display: grid;
  grid-template-columns: 52px 1fr;
  gap: 10px;
}
.stop-list li > span {
  width: 46px;
  min-height: 30px;
  border-radius: 6px;
  background: #edf2f7;
  display: grid;
  place-items: center;
  color: #415063;
  font-weight: 700;
  font-size: 12px;
}
.stop-list b {
  display: block;
}
.stop-list p {
  margin: 2px 0 0;
  color: #65717f;
  font-size: 13px;
}
</style>
