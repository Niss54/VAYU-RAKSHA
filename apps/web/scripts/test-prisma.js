const { PrismaClient } = require('@prisma/client');

async function testPrisma() {
  const connectionString = process.env.DATABASE_URL;
  console.log("Testing Prisma connection with Neon PostgreSQL...");
  console.log("connectionString is present:", Boolean(connectionString));
  
  const prisma = new PrismaClient();

  try {
    const users = await prisma.user.findMany();
    console.log("Prisma query success! Users count:", users.length);
    console.log("Found user:", users[0]?.email);

    const reports = await prisma.situationReport.findMany();
    console.log("Prisma reports count:", reports.length);
    console.log("Report district:", reports[0]?.district, "-", reports[0]?.summary);

    // Verify basic write/delete cycle
    const testLog = await prisma.auditLog.create({
      data: {
        action: "PRISMA_HEALTH_CHECK",
        userAgent: "NeonIntegration/Verification",
        ipAddress: "127.0.0.1",
      },
    });
    console.log("Health check write successful, id:", testLog.id);
    await prisma.auditLog.delete({ where: { id: testLog.id } });
    console.log("Health check cleanup successful.");

    await prisma.$disconnect();
    console.log(">>> PRISMA_NEON_VERIFIED_SUCCESSFULLY <<<");
  } catch (err) {
    console.error("Prisma error:", err);
    await prisma.$disconnect();
    process.exit(1);
  }
}

testPrisma();

