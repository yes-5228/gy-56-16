import { get, post } from "./http";

export const travelApi = {
  getAttractions: () => get("/attractions/"),
  getRoutes: () => get("/routes/"),
  getBookings: () => get("/bookings/"),
  getNotices: () => get("/notifications/"),
  createBooking: (payload) => post("/bookings/", payload),
  getPriceCalendar: (routeId, params = {}) => {
    const searchParams = new URLSearchParams(params).toString();
    const query = searchParams ? `?${searchParams}` : "";
    return get(`/routes/${routeId}/price-calendar/${query}`);
  },
  getPriceCalendarList: (params = {}) => {
    const searchParams = new URLSearchParams(params).toString();
    const query = searchParams ? `?${searchParams}` : "";
    return get(`/routes/price-calendar/${query}`);
  },
};
