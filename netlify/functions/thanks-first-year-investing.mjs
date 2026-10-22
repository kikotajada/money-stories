import { thanksFirstYearInvesting as template } from "../_templates.mjs";
import { handleThanks } from "../../src/thanks.js";

export default (request) =>
  handleThanks({ request, env: process.env }, { template, kitPath: "first-year-investing", expectedPlinkVar: "PLINK_FIRST_YEAR_INVESTING" });

export const config = { path: ["/first-year-investing/thanks", "/first-year-investing/thanks/"], method: "GET" };
