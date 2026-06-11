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
    <div class="progress-row">
      <span>已报名 {{ route.enrolled_count }}/{{ route.min_group_size }}</span>
      <div class="progress-track">
        <i :style="{ width: `${route.group_progress}%` }"></i>
      </div>
    </div>

    <div v-if="routeCalendar.length" class="calendar-preview">
      <p class="eyebrow">出行档期</p>
      <div class="date-chips">
        <span
          v-for="item in routeCalendar.slice(0, 4)"
          :key="item.id"
          :class="{ expired: isExpired(item) }"
        >
          {{ formatDate(item.travel_date) }}
          <em>¥{{ item.base_cost }}</em>
          <i v-if="isExpired(item)">已截止</i>
          <i v-else-if="item.remaining_inventory <= 0">已满</i>
          <i v-else>剩{{ item.remaining_inventory }}位</i>
        </span>
        <span v-if="routeCalendar.length > 4" class="more">
          +{{ routeCalendar.length - 4 }} 更多日期
        </span>
      </div>
    </div>
    <div v-else class="calendar-preview empty">
      <p class="eyebrow">出行档期</p>
      <p class="empty-hint">暂无价格日历，请使用线路基础费用</p>
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
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
}
.date-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.date-chips span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  background: #f0fdf4;
  color: #166534;
  font-size: 12px;
  font-weight: 600;
}
.date-chips span.expired {
  background: #fef2f2;
  color: #991b1b;
  text-decoration: line-through;
}
.date-chips span em {
  font-style: normal;
  color: #065f46;
  font-weight: 700;
}
.date-chips span.expired em {
  color: #7f1d1d;
}
.date-chips span i {
  font-style: normal;
  font-size: 11px;
  opacity: 0.85;
}
.date-chips span.more {
  background: #f1f5f9;
  color: #475569;
}
</style>
