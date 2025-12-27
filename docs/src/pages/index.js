import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Automated PDF Data Extraction using GenAI">
      <HomepageHeader />
      <main>
        {/* Use Cases Section */}
        <section className={clsx(styles.section, styles.sectionAlt)}>
          <div className="container">
            <h2 className={styles.sectionTitle}>Unlock Data from Documents</h2>
            <div className={styles.features}>
              <div className={styles.feature}>
                <div className={styles.featureIcon}>📊</div>
                <h3 className={styles.featureTitle}>Financial Reports</h3>
                <p>Extract tables, balance sheets, and KPIs from complex financial PDFs with high precision.</p>
              </div>
              <div className={styles.feature}>
                <div className={styles.featureIcon}>🧾</div>
                <h3 className={styles.featureTitle}>Invoices & Receipts</h3>
                <p>Automate the extraction of line items, totals, and vendor details from scanned documents.</p>
              </div>
              <div className={styles.feature}>
                <div className={styles.featureIcon}>🔬</div>
                <h3 className={styles.featureTitle}>Research & Technical</h3>
                <p>Digitize tables and experimental data from scientific papers for analysis.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Technology Section */}
        <section className={styles.section}>
          <div className="container">
            <h2 className={styles.sectionTitle}>Built with Advanced Tech</h2>
            <div className={styles.features}>
              <div className={styles.feature}>
                <div className={styles.featureIcon}>🤖</div>
                <h3 className={styles.featureTitle}>GenAI Powered</h3>
                <p>Leverages Google Gemini 1.5/2.0 to understand document layout and context like a human.</p>
              </div>
              <div className={styles.feature}>
                <div className={styles.featureIcon}>⚡</div>
                <h3 className={styles.featureTitle}>Multi-Agent System</h3>
                <p>Orchestrates specialized agents for scanning, extraction, aggregation, and exporting.</p>
              </div>
              <div className={styles.feature}>
                <div className={styles.featureIcon}>🔧</div>
                <h3 className={styles.featureTitle}>Fully Customizable</h3>
                <p>Define your own extraction schemas and prompts to suit any document type.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
