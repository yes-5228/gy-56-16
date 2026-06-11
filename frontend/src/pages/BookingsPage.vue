<template>
  <section class="booking-layout">
    <form class="booking-form" @submit.prevent="submit">
      <div>
        <p class="eyebrow">Registration</p>
        <h3>新增报名</h3>
      </div>
      <label>
        选择线路
        <select v-model.number="form.route" required @change="onRouteChange">
          <option disabled value="">请选择</option>
          <option v-for="route in routes" :key="route.id" :value="route.id">{{ route.title }}</option>
        </select>
      </label>

      <div v-if="selectedRoute && selectedCalendar.length" class="date-selector">
        <p class="eyebrow">选择出行日期</p>
        <div class="date-option-grid">
          <button
            v-for="item in selectedCalendar"
            :key="item.id"
            type="button"
            :class="{ active: selectedCalendarId === item.id, expired: isExpired(item), full: item.remaining_inventory <= 0 }"
            :disabled="isExpired(item) || item.remaining_inventory <= 0"
            @click="selectCalendarDate(item)"
          >
            <div class="opt-date">
              <strong>{{ getDayOfWeek(item.travel_date) }}</strong>
              <span>{{ formatDate(item.travel_date) }}</span>
            </div>
            <div class="opt-price">¥{{ item.base_cost }}</div>
            <div class="opt-status">
              <span v-if="isExpired(item)" class="expired-label">已截止</span>
              <span v-else-if="item.remaining_inventory <= 0" class="full-label">已满</span>
              <span v-else class="avail-label">剩{{ item.remaining_inventory }}位</span>
            </div>
            <div v-if="item.registration_deadline" class="opt-deadline">
              截止: {{ formatDateTime(item.registration_deadline) }}
            </div>
          </button>
        </div>
        <input type="hidden" v-model="form.travel_date" required />
      </div>

      <div v-else class="form-row">
        <label>
          人数
          <input v-model.number="form.party_size" min="1" type="number" required />
        </label>
        <label>
          出行日期
          <input v-model="form.travel_date" type="date" required />
        </label>
      </div>

      <div v-if="currentPricing" class="pricing-preview">
        <p class="eyebrow">费用预览</p>
        <div class="pricing-grid">
          <span>基础费用 <b>¥{{ currentPricing.base_cost }}</b></span>
          <span v-if="selectedRoute">导游服务 <b>¥{{ selectedRoute.guide_fee }}</b></span>
          <span v-if="selectedRoute">门票合计 <b>¥{{ selectedRoute.ticket_total }}</b></span>
        </div>
        <div class="pricing-total">
          <span>预计总价</span>
          <strong>¥{{ currentPricing.estimated_cost }}</strong>
        </div>
        <div v-if="selectedCalendarItem" class="pricing-stock">
          <span>该日期可报名</span>
          <strong>{{ selectedCalendarItem.remaining_inventory }} 位</strong>
        </div>
      </div>

      <label>
        联系人
        <input v-model="form.contact_name" required />
      </label>
      <label>
        手机号
        <input v-model="form.phone" required />
      </label>

      <div v-if="!selectedRoute || !selectedCalendar.length" class="form-row">
        <label>
          人数
          <input v-model.number="form.party_size" min="1" type="number" required />
        </label>
        <label>
          出行日期
          <input v-model="form.travel_date" type="date" required />
        </label>
      </div>
      <div v-else>
        <label>
          人数
          <input
            v-model.number="form.party_size"
            :min="1"
            :max="maxPartySize"
            type="number"
            required
          />
          <p v-if="selectedCalendarItem" class="hint">最多可报 {{ maxPartySize }} 人</p>
        </label>
      </div>

      <label>
        备注
        <textarea v-model="form.remark" rows="3"></textarea>
      </label>

      <button class="primary-action" type="submit" :disabled="!canSubmit">
        提交报名
      </button>
      <p v-if="submitError" class="error-msg">{{ submitError }}</p>
    </form>

    <section class="table-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Group Status</p>
          <h3>报名与成团状态</h3>
        </div>
        <span>{{ bookings.length }} 条报名</span>
      </div>
      <div class="booking-list">
        <article v-for="booking in bookings" :key="booking.id">
          <div>
            <h4>{{ booking.contact_name }} · {{ booking.party_size }} 人</h4>
            <p>{{ booking.route_title }} / {{ booking.travel_date }}</p>
            <p v-if="booking.travel_base_cost" class="price-info">
              单价 ¥{{ booking.travel_base_cost }} · 剩余 {{ booking.travel_remaining }} 位
            </p>
          </div>
          <span class="tag">{{ booking.status_label }}</span>
          <div class="booking-progress">
            <strong>{{ booking.date_enrolled }}/{{ booking.min_group_size }}</strong>
            <div class="progress-track small">
              <i :style="{ width: `${booking.date_progress}%` }"></i>
            </div>
            <p class="progress-label">该日成团进度</p>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";

const props = defineProps({
  routes: { type: Array, required: true },
  priceCalendar: { type: Array, default: () => [] },
  bookings: { type: Array, required: true },
});

const emit = defineEmits(["booking-created"]);

const form = reactive({
  route: "",
  contact_name: "",
  phone: "",
  party_size: 1,
  travel_date: "",
  status: "pending",
  remark: "",
});

const selectedCalendarId = ref(null);
const submitError = ref("");

const selectedRoute = computed(() => {
  if (!form.route) return null;
  return props.routes.find((r) => r.id === form.route) || null;
});

const selectedCalendar = computed(() => {
  if (!selectedRoute.value) return [];
  const routeId = selectedRoute.value.id;
  return props.priceCalendar
    .filter((item) => item.route === routeId || item.route_id === routeId)
    .sort((a, b) => new Date(a.travel_date) - new Date(b.travel_date));
});

const selectedCalendarItem = computed(() => {
  return selectedCalendar.value.find((item) => item.id === selectedCalendarId.value) || null;
});

const currentPricing = computed(() => {
  if (!selectedRoute.value) return null;
  if (selectedCalendarItem.value) {
    const base = Number(selectedCalendarItem.value.base_cost);
    const guide = Number(selectedRoute.value.guide_fee);
    const ticket = Number(selectedRoute.value.ticket_total);
    return {
      base_cost: selectedCalendarItem.value.base_cost,
      estimated_cost: (base + guide + ticket).toFixed(2),
    };
  }
  return {
    base_cost: selectedRoute.value.base_cost,
    estimated_cost: selectedRoute.value.estimated_cost,
  };
});

const maxPartySize = computed(() => {
  if (selectedCalendarItem.value) {
    return selectedCalendarItem.value.remaining_inventory;
  }
  if (selectedRoute.value) {
    return selectedRoute.value.max_group_size;
  }
  return 999;
});

const canSubmit = computed(() => {
  if (selectedCalendar.value.length > 0 && !selectedCalendarId.value) {
    return false;
  }
  return true;
});

watch(selectedRoute, (newRoute) => {
  selectedCalendarId.value = null;
  form.travel_date = "";
  submitError.value = "";
  if (newRoute && selectedCalendar.value.length > 0) {
    const firstAvailable = selectedCalendar.value.find((item) => !isExpired(item) && item.remaining_inventory > 0);
    if (firstAvailable) {
      selectCalendarDate(firstAvailable);
    }
  }
});

function onRouteChange() {
}

function selectCalendarDate(item) {
  if (!isExpired(item) && item.remaining_inventory > 0) {
    selectedCalendarId.value = item.id;
    form.travel_date = item.travel_date;
    submitError.value = "";
    if (form.party_size > item.remaining_inventory) {
      form.party_size = item.remaining_inventory;
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

async function submit() {
  submitError.value = "";
  if (selectedCalendar.value.length > 0 && !selectedCalendarId.value) {
    submitError.value = "请选择出行日期";
    return;
  }
  const savedCalendarId = selectedCalendarId.value;
  const savedTravelDate = form.travel_date;
  try {
    emit("booking-created", { ...form });
    form.contact_name = "";
    form.phone = "";
    form.party_size = 1;
    form.remark = "";
    selectedCalendarId.value = savedCalendarId;
    form.travel_date = savedTravelDate;
  } catch (err) {
    submitError.value = err.message || "提交失败，请重试";
  }
}
</script>

<style scoped>
.date-selector {
  display: grid;
  gap: 8px;
}
.date-option-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.date-option-grid button {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  background: white;
  text-align: left;
  display: grid;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.date-option-grid button:hover:not(:disabled) {
  border-color: #0f766e;
}
.date-option-grid button.active {
  border-color: #0f766e;
  background: #f0fdfa;
}
.date-option-grid button.expired,
.date-option-grid button.full {
  opacity: 0.5;
  cursor: not-allowed;
}
.date-option-grid button.expired {
  background: #fef2f2;
}
.date-option-grid button.full {
  background: #fef3c7;
}
.opt-date {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.opt-date strong {
  font-size: 13px;
  color: #17202a;
}
.opt-date span {
  font-size: 12px;
  color: #65717f;
  font-weight: 600;
}
.opt-price {
  font-size: 18px;
  font-weight: 700;
  color: #0f766e;
}
.opt-status .expired-label {
  color: #991b1b;
  font-size: 11px;
  font-weight: 700;
}
.opt-status .full-label {
  color: #92400e;
  font-size: 11px;
  font-weight: 700;
}
.opt-status .avail-label {
  color: #166534;
  font-size: 11px;
  font-weight: 700;
}
.opt-deadline {
  font-size: 10px;
  color: #94a3b8;
}
.pricing-preview {
  background: #f8fafc;
  border-radius: 8px;
  padding: 14px;
  display: grid;
  gap: 10px;
}
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.pricing-grid span {
  font-size: 12px;
  color: #65717f;
}
.pricing-grid b {
  display: block;
  color: #17202a;
  font-size: 14px;
}
.pricing-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px dashed #cbd5e1;
}
.pricing-total span {
  font-size: 13px;
  color: #475569;
  font-weight: 600;
}
.pricing-total strong {
  font-size: 20px;
  color: #0f766e;
}
.pricing-stock {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pricing-stock span {
  font-size: 13px;
  color: #64748b;
}
.pricing-stock strong {
  font-size: 16px;
  color: #0369a1;
}
.hint {
  margin: 4px 0 0;
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
}
.error-msg {
  margin: 0;
  color: #b91c1c;
  font-size: 13px;
}
.price-info {
  margin: 4px 0 0 !important;
  font-size: 12px;
  color: #0f766e;
  font-weight: 600;
}
.booking-progress {
  display: grid;
  gap: 4px;
  text-align: right;
  min-width: 110px;
}
.booking-progress strong {
  font-size: 15px;
  color: #17202a;
}
.progress-track.small {
  height: 6px;
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
.progress-label {
  margin: 0;
  font-size: 11px;
  color: #94a3b8;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
