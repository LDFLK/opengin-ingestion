import Link from "next/link";
import { Database, Network, FileJson, Table, Activity } from "lucide-react";

export default function Home() {
  const features = [
    {
      name: "Entities",
      description: "Manage core entities and their definitions.",
      href: "/entity",
      icon: Database,
      color: "bg-blue-500",
    },
    {
      name: "Relationships",
      description: "Connect entities to define the graph structure.",
      href: "/relationship",
      icon: Network,
      color: "bg-indigo-500",
    },
    {
      name: "Metadata",
      description: "Add flexible JSON metadata to entities.",
      href: "/metadata",
      icon: FileJson,
      color: "bg-purple-500",
    },
    {
      name: "Attributes",
      description: "Define time-based attributes for entities.",
      href: "/attribute",
      icon: Table,
      color: "bg-pink-500",
    },
    {
      name: "Xplore",
      description: "Visualize and explore the OpenGIN graph.",
      href: "/xplore",
      icon: Activity,
      color: "bg-orange-500",
    },
  ];

  return (
    <div className="space-y-12">
      <div className="text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-5xl md:text-6xl">
          <span className="block">Welcome to</span>
          <span className="block text-indigo-600">OpenGIN Ingestion</span>
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 dark:text-gray-400 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          The Universal Data Engine for managing complex entity relationships and temporal data.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((feature) => (
          <Link
            key={feature.name}
            href={feature.href}
            className="relative group bg-white dark:bg-gray-800 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <div>
              <span
                className={`rounded-lg inline-flex p-3 ring-4 ring-white dark:ring-gray-800 ${feature.color} text-white`}
              >
                <feature.icon className="h-6 w-6" aria-hidden="true" />
              </span>
            </div>
            <div className="mt-8">
              <h3 className="text-lg font-medium">
                <span className="absolute inset-0" aria-hidden="true" />
                {feature.name}
              </h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                {feature.description}
              </p>
            </div>
            <span
              className="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
              aria-hidden="true"
            >
              <svg
                className="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
              </svg>
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
