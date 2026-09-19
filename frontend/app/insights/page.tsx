import { redirect } from "next/navigation";

/**
 * Insights became Analytics when the product grew past inventory alone.
 * Redirect rather than delete: an old bookmark should still land somewhere.
 */
export default function InsightsRedirect() {
  redirect("/analytics");
}
