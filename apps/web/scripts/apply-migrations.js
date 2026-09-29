const { neon } = require('@neondatabase/serverless');

const statements = [
  // 1. Enums
  `DO $$ BEGIN
    CREATE TYPE "Role" AS ENUM ('USER', 'ADMIN', 'SUPER_ADMIN', 'OFFICER', 'VOLUNTEER');
  EXCEPTION
    WHEN duplicate_object THEN null;
  END $$;`,

  `DO $$ BEGIN
    CREATE TYPE "Status" AS ENUM ('ACTIVE', 'INACTIVE', 'DELETED', 'PENDING', 'TRIGGERED', 'COMPLETED');
  EXCEPTION
    WHEN duplicate_object THEN null;
  END $$;`,

  // 2. Users Table
  `CREATE TABLE IF NOT EXISTS "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password_hash" TEXT,
    "name" TEXT NOT NULL,
    "avatar_url" TEXT,
    "role" "Role" NOT NULL DEFAULT 'USER',
    "is_verified" BOOLEAN NOT NULL DEFAULT false,
    "verify_token" TEXT,
    "reset_token" TEXT,
    "reset_expires" TIMESTAMP(3),
    "last_login_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
  );`,

  `CREATE UNIQUE INDEX IF NOT EXISTS "users_email_key" ON "users"("email");`,
  `CREATE UNIQUE INDEX IF NOT EXISTS "users_verify_token_key" ON "users"("verify_token");`,
  `CREATE UNIQUE INDEX IF NOT EXISTS "users_reset_token_key" ON "users"("reset_token");`,
  `CREATE INDEX IF NOT EXISTS "idx_users_email" ON "users"("email");`,

  // 3. Sessions Table
  `CREATE TABLE IF NOT EXISTS "sessions" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "refresh_token" TEXT NOT NULL,
    "user_agent" TEXT,
    "ip_address" TEXT,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "sessions_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE
  );`,

  `CREATE UNIQUE INDEX IF NOT EXISTS "sessions_refresh_token_key" ON "sessions"("refresh_token");`,
  `CREATE INDEX IF NOT EXISTS "idx_sessions_user_id" ON "sessions"("user_id");`,
  `CREATE INDEX IF NOT EXISTS "idx_sessions_refresh_token" ON "sessions"("refresh_token");`,

  // 4. Situation Reports Table
  `CREATE TABLE IF NOT EXISTS "situation_reports" (
    "id" TEXT NOT NULL,
    "user_id" TEXT,
    "district" TEXT NOT NULL,
    "cyclone_name" TEXT NOT NULL DEFAULT 'AMPHAN-26',
    "severity" TEXT NOT NULL DEFAULT 'HIGH',
    "status" "Status" NOT NULL DEFAULT 'ACTIVE',
    "summary" TEXT NOT NULL,
    "affected_pop" INTEGER,
    "power_outage" BOOLEAN NOT NULL DEFAULT false,
    "telecom_down" BOOLEAN NOT NULL DEFAULT false,
    "coordinates" JSONB,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "situation_reports_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "situation_reports_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE
  );`,

  `CREATE INDEX IF NOT EXISTS "idx_situation_reports_district" ON "situation_reports"("district");`,
  `CREATE INDEX IF NOT EXISTS "idx_situation_reports_status" ON "situation_reports"("status");`,
  `CREATE INDEX IF NOT EXISTS "idx_situation_reports_severity" ON "situation_reports"("severity");`,
  `CREATE INDEX IF NOT EXISTS "idx_situation_reports_created_at" ON "situation_reports"("created_at");`,

  // 5. Audit Logs Table
  `CREATE TABLE IF NOT EXISTS "audit_logs" (
    "id" TEXT NOT NULL,
    "user_id" TEXT,
    "action" TEXT NOT NULL,
    "table_name" TEXT,
    "record_id" TEXT,
    "old_value" JSONB,
    "new_value" JSONB,
    "ip_address" TEXT,
    "user_agent" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "audit_logs_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "audit_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE
  );`,

  `CREATE INDEX IF NOT EXISTS "idx_audit_logs_user_id" ON "audit_logs"("user_id");`,
  `CREATE INDEX IF NOT EXISTS "idx_audit_logs_action" ON "audit_logs"("action");`,
  `CREATE INDEX IF NOT EXISTS "idx_audit_logs_created_at" ON "audit_logs"("created_at");`,

  // 6. Donations Table (Razorpay)
  `CREATE TABLE IF NOT EXISTS "donations" (
    "id" TEXT NOT NULL,
    "user_id" TEXT,
    "donor_name" TEXT NOT NULL,
    "donor_email" TEXT NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "currency" TEXT NOT NULL DEFAULT 'INR',
    "razorpay_order_id" TEXT NOT NULL,
    "razorpay_payment_id" TEXT,
    "razorpay_signature" TEXT,
    "status" TEXT NOT NULL DEFAULT 'created',
    "campaign" TEXT NOT NULL DEFAULT 'SDRF-ODISHA-RELIEF',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "donations_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "donations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE
  );`,

  `CREATE UNIQUE INDEX IF NOT EXISTS "donations_razorpay_order_id_key" ON "donations"("razorpay_order_id");`,
  `CREATE UNIQUE INDEX IF NOT EXISTS "donations_razorpay_payment_id_key" ON "donations"("razorpay_payment_id");`,
  `CREATE INDEX IF NOT EXISTS "idx_donations_donor_email" ON "donations"("donor_email");`,
  `CREATE INDEX IF NOT EXISTS "idx_donations_status" ON "donations"("status");`,
  `CREATE INDEX IF NOT EXISTS "idx_donations_created_at" ON "donations"("created_at");`,

  // 7. Parametric Disbursements Table
  `CREATE TABLE IF NOT EXISTS "parametric_disbursements" (
    "id" TEXT NOT NULL,
    "beneficiary_name" TEXT NOT NULL,
    "beneficiary_vpa" TEXT NOT NULL,
    "aadhaar_last4" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "trigger_condition" TEXT NOT NULL,
    "status" "Status" NOT NULL DEFAULT 'TRIGGERED',
    "payout_tx_id" TEXT,
    "triggered_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "disbursed_at" TIMESTAMP(3),
    CONSTRAINT "parametric_disbursements_pkey" PRIMARY KEY ("id")
  );`,

  `CREATE UNIQUE INDEX IF NOT EXISTS "parametric_disbursements_payout_tx_id_key" ON "parametric_disbursements"("payout_tx_id");`,
  `CREATE INDEX IF NOT EXISTS "idx_disbursements_district" ON "parametric_disbursements"("district");`,
  `CREATE INDEX IF NOT EXISTS "idx_disbursements_status" ON "parametric_disbursements"("status");`,
  `CREATE INDEX IF NOT EXISTS "idx_disbursements_triggered_at" ON "parametric_disbursements"("triggered_at");`,

  // 8. Prisma migration tracking table
  `CREATE TABLE IF NOT EXISTS "_prisma_migrations" (
    "id" VARCHAR(36) NOT NULL,
    "checksum" VARCHAR(64) NOT NULL,
    "finished_at" TIMESTAMPTZ,
    "migration_name" VARCHAR(255) NOT NULL,
    "logs" TEXT,
    "rolled_back_at" TIMESTAMPTZ,
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "applied_steps_count" INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT "_prisma_migrations_pkey" PRIMARY KEY ("id")
  );`
];

async function applyMigrations() {
  const url = process.env.DATABASE_URL;
  if (!url) {
    console.error("DATABASE_URL missing!");
    process.exit(1);
  }

  console.log("Applying Neon PostgreSQL migrations...");
  const sql = neon(url);

  try {
    for (let i = 0; i < statements.length; i++) {
      const stmt = statements[i].trim();
      if (stmt) {
        await sql.query(stmt);
      }
    }
    console.log("All schema tables, enums, constraints, and indexes created successfully!");

    // Record migration in _prisma_migrations
    const migrationId = "20260929235000_init_vayu_raksha_neon";
    await sql`
      INSERT INTO "_prisma_migrations" ("id", "checksum", "finished_at", "migration_name", "applied_steps_count")
      VALUES (${migrationId}, 'initial_neon_migration_vayu_raksha', NOW(), '0_init_vayu_raksha', 8)
      ON CONFLICT ("id") DO NOTHING;
    `;

    // Seed default admin user and initial report if empty
    const usersCount = await sql`SELECT count(*)::int as count FROM "users";`;
    if (usersCount[0].count === 0) {
      console.log("Seeding initial data...");
      await sql`
        INSERT INTO "users" ("id", "email", "name", "role", "is_verified")
        VALUES ('usr_admin_synth', 'admin@syntrix.vayu.gov.in', 'VAYU-RAKSHA Super Admin', 'SUPER_ADMIN', true)
        ON CONFLICT ("email") DO NOTHING;
      `;
      
      await sql`
        INSERT INTO "situation_reports" ("id", "district", "cyclone_name", "severity", "status", "summary", "affected_pop", "power_outage", "telecom_down")
        VALUES ('rep_amphan_puri_01', 'Puri', 'AMPHAN-26', 'CRITICAL', 'ACTIVE', 'Severe storm surge anticipated across coastal blocks. 18 SDRF teams deployed with emergency power backups.', 420000, true, false)
        ON CONFLICT ("id") DO NOTHING;
      `;
      console.log("Initial seed data inserted.");
    }

    // List all tables
    const tables = await sql`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name;
    `;
    console.log(">>> MIGRATION SUCCESSFUL <<<");
    console.log("Current Tables in Neon PostgreSQL:", tables.map(t => t.table_name));

  } catch (error) {
    console.error("Migration error:", error);
    process.exit(1);
  }
}

applyMigrations();
