// src/composables/useSpatialBiasApi.ts
import api from '@/api/axios'
import { schemas } from '@/api/client'   
import { ZodError } from "zod";
import axios from "axios";

function formatFastapi422(data: any) {
  const items = Array.isArray(data?.detail) ? data.detail : [];
  if (!items.length) return "Invalid request.";
  const toPath = (loc: (string|number)[]) =>
    loc
      .filter((x) => x !== "body")
      .map((seg, i) => (typeof seg === "number" ? `[${seg}]` : i ? `.${seg}` : String(seg)))
      .join("");
  return "Request validation failed:\n- " +
    items.map((e: any) => `${toPath(e.loc)}: ${e.msg}`).join("\n- ");
}

const pathToString = (path: (string | number)[]) =>
  path.reduce((acc, seg, i) => {
    if (typeof seg === "number") return `${acc}[${seg}]`;
    return acc ? `${acc}.${seg}` : seg;
  }, "");

export function formatZod(err: ZodError) {
  const lines = err.issues.map((i: ZodIssue) => {
    // Make missing fields read nicely
    const isMissing =
      i.code === "invalid_type" && (i as any).received === "undefined";
    const msg = isMissing || i.message === "Required" ? "Field required" : i.message;
    return `${pathToString(i.path)}: ${msg}`;
  });
  return "Client-side validation failed:\n- " + lines.join("\n- ");
}

export function useSpatialBiasApi() {
  async function runAnalysis({
    mode,
    advanced,
    indivInfoParsed,
    regionInfoParsed,
    fitIndivParsed,
    predictIndivParsed,
    predictRegionParsed,
  }: {
    mode: 'audit' | 'relabel' | 'threshold',
    advanced: any,
    indivInfoParsed: any[],
    regionInfoParsed: any[],
    fitIndivParsed: any[],
    predictIndivParsed: any[],
    predictRegionParsed: any[],
  }): Promise<any> {

    try {
      if (mode === 'audit') {
        const payload = {
          indiv_info: indivInfoParsed,
          region_info: regionInfoParsed.length ? regionInfoParsed : undefined,
          equal_opp: advanced.equal_opp,
          signif_level: advanced.signif_level,
          n_worlds: advanced.n_worlds,
        }

        const body = schemas.AuditRequest.parse(payload)
        const { data } = await api.post('/api/spatial-bias/audit', body)
        return data
      }

      if (mode === 'relabel') {
        const payload = {
          indiv_info: indivInfoParsed,
          region_info: regionInfoParsed.length ? regionInfoParsed : undefined,
          equal_opp: advanced.equal_opp,
          signif_level: advanced.signif_level,
          n_worlds: advanced.n_worlds,
          budget_constr: advanced.budget_constr,
          pr_constr: advanced.pr_constr,
          approx: advanced.approx,
          work_limit: advanced.wlimit,
        }

        const body = schemas.RelabelingRequest.parse(payload)
        const { data } = await api.post('/api/spatial-bias/mitigate/relabel', body)
        return data
      }

      if (mode === 'threshold') {
        if (!fitIndivParsed.length || !predictIndivParsed.length) {
          throw new Error("Missing required threshold mitigation inputs: fit_indiv_info and predict_indiv_info")
        }

        const payload = {
          fit_indiv_info: fitIndivParsed,
          predict_indiv_info: predictIndivParsed,
          predict_region_info: predictRegionParsed.length > 0 ? predictRegionParsed : undefined,
          approx: advanced.approx,
          equal_opp: advanced.equal_opp,
          signif_level: advanced.signif_level,
          n_worlds: advanced.n_worlds,
          budget_constr: advanced.budget_constr,
          pr_constr: advanced.pr_constr,
          work_limit: advanced.wlimit,
          default_boundary: advanced.decision_bound
        }

        const body = (schemas as any).ThresholdAdjustmentRequest.parse(payload)
        const { data } = await api.post('/api/spatial-bias/mitigate/threshold', body)
        return data
      }

      throw new Error("Invalid mode")
    } catch (err: any) {
      console.log("Error in useSpatialBiasApi:", err);
      console.log("Error details:", err.response?.data || err.message || err);
      console.log("err.response?.status:", err.response?.status);
      if (err instanceof ZodError) {
        throw new Error(formatZod(err));
      }
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        console.log('API Validation Error:', err.response.data);
        throw new Error(formatFastapi422(err.response.data));
      }
      throw err;
    }
  }

  return { runAnalysis }
}
