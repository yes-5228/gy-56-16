<template>
  <article class="route-card" @click="$emit('view-detail', route)">
    <div class="route-head">
      <div>
        <p class="eyebrow">{{ route.city }} · {{ route.days }} 天</p>
        <h3>{{ route.title }}</h3>
      </div>
      <span class="tag">{{ route.status_label }}</span>
    </div>
    <p class="description">{{ route.description }}</p>
    <div class="budget-grid">
      <span>基础费用 <b>¥{{ displayPrice.base_cost }}</b></span>
      <span>门票合计 <b>¥{{ route.ticket_total }}</b></span>
      <span>预计总价 <b>¥{{ displayPrice.estimated_cost }}</b></span>
    </div>

    <div v-if="routeCalendar.length" class="calendar-preview">
      <p class="eyebrow">出行档期（按日期成团）</p>
      <div class="date-list">
        <div
          v-for="item in routeCalendar.slice(0, 4)"
          :key="item.id"
          :class="{ expired: isExpired(item) }"
          class="date-item"
        >
          <div class="date-head">
            <span class="date-label">{{ formatDate(item.travel_date) }}</span>
            <span class="price-label">¥{{ item.base_cost }}</span>
          </div>
          <div class="date-progress">
            <div class="progress-info">
              <span>
                <i v-if="isExpired(item)" class="expired-tag">已截止</i>
                <i v-else-if="item.remaining_inventory <= 0" class="full-tag">已满</i>
                <i v-else>{{ item.enrolled_count }}/{{ route.min_group_size }} 成团</i>
              </span>
              <span class="stock-info">剩{{ item.remaining_inventory }}位</span>
            </div>
            <div class="progress-track small">
              <i :style="{ width: `${getProgress(item)}%` }"></i>
            </div>
          </div>
        </div>
        <div v-if="routeCalendar.length > 4" class="more-item">
          +{{ routeCalendar.length - 4 }} 更多日期，点击查看详情
        </div>
      </div>
    </div>
    <div v-else class="calendar-preview empty">
      <p class="eyebrow">出行档期</p>
      <div class="progress-row">
        <span>已报名 {{ route.enrolled_count }}/{{ route.min_group_size }}</span>
        <div class="progress-track">
          <i :style="{ width: `${route.group_progress}%` }"></i>
        </div>
      </div>
      <p class="empty-hint">暂无价格日历，使用线路统一价格</p>
    </div>

    <ol class="stop-list">
      <li v-for="stop in route.stops" :key="stop.id">
        <span>D{{ stop.day }}-{{ stop.order }}</span>
        <div>
          <b>{{ stop.attraction.name }}</b>
          <p>{{ stop.note }}</p>
        </div>
      </li>
    </ol>
  </article>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  route: { type: Object, required: true },
  priceCalendar: { type: Array, default: () => [] },
});

defineEmits(["view-detail"]);

const routeCalendar = computed(() => {
  return props.priceCalendar
    .filter((item) => item.route === props.route.id || item.route_id === props.route.id)
    .sort((a, b) => new Date(a.travel_date) - new Date(b.travel_date));
});

const displayPrice = computed(() => {
  const upcoming = routeCalendar.value.find((item) => !isExpired(item));
  if (upcoming) {
    const estimated = Number(upcoming.base_cost) + Number(props.route.guide_fee) + Number(props.route.ticket_total);
    return {
      base_cost: upcoming.base_cost,
      estimated_cost: estimated.toFixed(2),
    };
  }
  return {
    base_cost: props.route.base_cost,
    estimated_cost: props.route.estimated_cost,
  };
});

function getProgress(item) {
  if (props.route.min_group_size === 0) return 100;
  return Math.min(Math.round((item.enrolled_count / props.route.min_group_size) * 100), 100);
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
</script>

<style scoped>
.route-card {
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}
.route-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}
.calendar-preview {
  display: grid;
  gap: 8px;
}
.calendar-preview.empty .empty-hint {
  margin: 8px 0 0;
  color: #94a3b8;
  font-size: 13px;
}
.date-list {
  display: grid;
  gap: 10px;
}
.date-item {
  display: grid;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}
.date-item.expired {
  background: #fef2f2;
  border-color: #fecaca;
  opacity: 0.75;
}
.date-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.date-label {
  font-size: 13px;
  font-weight: 700;
  color: #17202a;
}
.price-label {
  font-size: 15px;
  font-weight: 700;
  color: #0f766e;
}
.date-progress {
  display: grid;
  gap: 6px;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}
.progress-info i {
  font-style: normal;
  font-weight: 600;
}
.progress-info .expired-tag {
  color: #991b1b;
}
.progress-info .full-tag {
  color: #92400e;
}
.stock-info {
  color: #0369a1;
  font-weight: 600;
}
.progress-track.small {
  height: 5px;
  border-radius: 3px;
  background: #e2e8f0;
  overflow: hidden;
}
.progress-track.small i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #14b8a6, #0f766e);
  border-radius: 3px;
  transition: width 0.4s ease;
}
.date-item.expired .progress-track.small i {
  background: linear-gradient(90deg, #ef4444, #b91c1c);
}
.more-item {
  padding: 10px;
  border-radius: 8px;
  background: #f1f5f9;
  color: #475569;
  font-size: 13px;
  text-align: center;
  font-weight: 500;
}
.progress-row {
  display: grid;
  gap: 8px;
}
.progress-row > span {
  font-size: 13px;
  font-weight: 600;
  color: #415063;
}
.progress-track {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #e2e8f0;
  overflow: hidden;
}
.progress-track i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #14b8a6, #0f766e);
  border-radius: 4px;
  transition: width 0.4s ease;
}
</style>
