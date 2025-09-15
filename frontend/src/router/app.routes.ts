import { HomeView } from "../views";
import SpatialBias from "@/views/SpatialBias.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    meta: { icon: "HomeIcon" },
    component: HomeView,
    },

    {
      path: "/spatial-bias",
      name: "Spatial Bias",
      component: SpatialBias,
      meta: {
        icon: "CogIcon", description: "Audit and mitigate spatial bias in ML predictions",
      },
    },

  {
    path: "/services",
    name: "Services",
    meta: { icon: "CogIcon" },
    //component: HomeView,
    children: [
      {
        path: "data-services",
        name: "Data Services",
        //component: HomeView, // Instead of creating the empty path we can conditionally render parent content.
        children: [
          {
            path: "", // Exact match for /services/data-services
            name: " ",
            component: HomeView,
          },
          {
            path: ":dataFeatureToolkit",
            name: "Data Feature Toolkit",
            component: HomeView,
            meta: {
              description: "Feature operations for your analytics",
            },
          },
        ],
      },
      {
        path: "analytics",
        name: "Data Analytics",
        component: HomeView,
      },
    ],
  },
  {
    path: "/pipelines",
    name: "Pipelines",
    component: HomeView,
  },
  {
    path: "/assets",
    name: "Assets",
    component: HomeView,
  },
  {
    path: "/models",
    name: "Models",
    component: HomeView,
    children: [
      {
        path: "data",
        name: "Data Models",

        component: HomeView,
      },
      {
        path: "analytics",
        name: "Analytics Models",
        component: HomeView,
      },
    ],
  },
  {
    path: "/*",
    redirect: { path: "/" },
  },
];

export default routes;
