const { neon } = require('@neondatabase/serverless');

async function testConnection() {
  const url = process.env.DATABASE_URL;
  if (!url) {
    console.error("ERROR: DATABASE_URL is not defined in environment");
    process.exit(1);
  }
  
  console.log("Connecting to Neon PostgreSQL production database...");
  console.log("Target host:", url.split('@')[1]?.split('/')[0] || "hidden");
  
  try {
    const sql = neon(url);
    const result = await sql`SELECT 1 as connected, NOW() as server_time, version() as pg_version;`;
    console.log(">>> NEON_POSTGRES_CONNECTED_SUCCESSFULLY <<<");
    console.log("Query Result:", JSON.stringify(result, null, 2));
    
    // Check tables in public schema
    const tables = await sql`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name;
    `;
    console.log("Existing Tables:", tables.map(t => t.table_name));
  } catch (err) {
    console.error("Connection failed:", err.message);
    process.exit(1);
  }
}

testConnection();
