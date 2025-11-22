"use strict";

const fs = require("fs");
const path = require("path");
const ASSAYS = [
    {
        key: "Endotoxin",
        file: "endotoxin.csv",
        cols: ["spikeRecovery", "endotoxin"]
    },
    {
        key: "NTA",
        file: "nta.csv",
        cols: [
            "particleSizeMeanNanoparticleTrackingAnalysis",
            "particleSizeModeNanoparticleTrackingAnalysis",
            "d90NanoparticleTrackingAnalysis",
            "d50NanoparticleTrackingAnalysis",
            "d10NanoparticleTrackingAnalysis",
            "spanNanoparticleTrackingAnalysis"
        ]
    },
    {
        key: "TNS",
        file: "tns.csv",
        cols: [
            "apparentPkaTNSAssay",
            "lowerConfidenceInterval",
            "upperConfidenceInterval"
        ]
    },
    {
        key: "AEX_Accessible_mRNA",
        file: "aex_accessible_mrna.csv",
        cols: [
            "enantiomericExcessPercentAEX",
            "accessibleMRNAEnantiomericExcessEnzymeDigestPositive",
            "accessibleMRNAEnantiomericExcessEnzymeDigestNegative"
        ]
    },
    {
        key: "Ribostar",
        file: "ribostar.csv",
        cols: ["enantiomericExcessRiboSTAR"]
    },
    {
        key: "Sticky_Heparin_Sepharose_Binding",
        file: "sticky_heparin_sepharose_binding.csv",
        cols: [
            "relativePercentAreaOfBoundLNPsStickyAssay",
            "relativePercentAreaOfBoundLNPsStickyAssayEnzymeDigestPositive",
            "relativePercentAreaOfBoundLNPsStickyAssayEnzymeDigestNegative"
        ]
    },
    {
        key: "Circular_Dichroism",
        file: "circular_dichroism.csv",
        cols: ["circularDichroismLambdaMax", "circularDichroismSignalMax"]
    },
    {
        key: "BEEFI",
        file: "beefi.csv",
        cols: [
            "serumPercentEnantiomericExcessBEEFI",
            "mRNAReleasePercentBEEFI",
            "serumPercentEnantiomericExcessBEEFIEnzymeDigestPositive",
            "serumPercentEnantiomericExcessBEEFIDigestNegative"
        ]
    },
    {
        key: "Generalized_Polarity",
        file: "generalized_polarity.csv",
        cols: [
            "fluorescenceGeneralizedPolarizationValue",
            "fluorescenceGeneralizedPolarizationValueStandardDeviation"
        ]
    },
    {
        key: "Peg_Shedding",
        file: "peg_shedding.csv",
        cols: [
            "percentPEGat8hoursPEGShedding",
            "timeAt50percentPEGShedPEGShedding"
        ]
    },
    {
        key: "Zeta_Potential",
        file: "zeta_potential.csv",
        cols: ["zetaPotential", "zetaPotentialStandardDeviation"]
    }
];
module.exports = ($sequelize, $Sequelize, QCReport) => {
    return class {
        constructor() {
            this._queryInterface = $sequelize.getQueryInterface();
            this.sequelize = $Sequelize;
            const { Op } = $Sequelize;
            this.Op = Op;
            this.closeSequelize = false
        }

        async upAsync() {
            const outDir = path.resolve(process.cwd(), "assay-exports");
            if (!fs.existsSync(outDir))
                fs.mkdirSync(outDir, { recursive: true });

            const EOL = "\r\n"; // friendlier for Excel on Windows
            const writers = new Map();

            const addBOM = true; // set false if you don’t want BOM
            const makeHeader = cols => ["assayId", "fbId", ...cols].join(",");

            const safeCell = v => {
                if (v === null || v === undefined) return "";
                // Format Dates explicitly
                if (v instanceof Date) return v.toISOString();
                // Keep BigInt precise by stringifying
                const s = typeof v === "bigint" ? v.toString() : String(v);
                // Mitigate CSV injection when opening in spreadsheet apps
                const startsDanger = /^[=+\-@]/.test(s);
                const escaped = /[",\n\r]/.test(s)
                    ? `"${s.replace(/"/g, '""')}"`
                    : s;
                return startsDanger ? `'${escaped}` : escaped;
            };

            const openWriter = (file, cols) => {
                const tmp = path.join(outDir, `${file}.tmp`);
                const finalPath = path.join(outDir, file);
                const ws = fs.createWriteStream(tmp, {
                    encoding: "utf8",
                    flags: "w"
                });

                ws.on("error", err => {
                    // surface and fail fast
                    throw err;
                });

                if (addBOM) ws.write("\uFEFF"); // UTF-8 BOM for Excel
                ws.write(makeHeader(cols) + EOL);

                writers.set(file, { ws, tmp, finalPath });
                return ws;
            };

            for (const a of ASSAYS) openWriter(a.file, a.cols);

            const ALL_COLS = Array.from(new Set(ASSAYS.flatMap(a => a.cols)));

            const CHUNK = 5000;
            let lastId = 0n; // use BigInt in case your PK is bigint
            let total = 0;

            try {
                while (true) {
                    const rows = await QCReport.findAll({
                        where: { id: { [this.Op.gt]: lastId } },
                        order: [["id", "ASC"]],
                        limit: CHUNK,
                        raw: true,
                        hooks: false,
                    });

                    if (!rows.length) break;

                    for (const r of rows) {
                        const assayId = r.id;
                        const fbId = r.formulationBatchId;

                        for (const a of ASSAYS) {
                            const hasAny = a.cols.some(
                                c => r[c] !== null && r[c] !== undefined
                            );
                            if (!hasAny) continue;

                            const values = a.cols.map(c => safeCell(r[c]));
                            const line =
                                [
                                    safeCell(assayId),
                                    safeCell(fbId),
                                    ...values
                                ].join(",") + EOL;

                            const writer = writers.get(a.file).ws;
                            const ok = writer.write(line);
                            if (!ok) {
                                await new Promise(res =>
                                    writer.once("drain", res)
                                );
                            }
                        }
                    }

                    total += rows.length;
                    const last = rows[rows.length - 1].id;
                    // normalize lastId to BigInt if it isn't already
                    lastId = typeof last === "bigint" ? last : BigInt(last);
                    if (total % (CHUNK * 5) === 0) {
                        console.log(`Processed ${total} rows...`);
                    }
                }

                console.log(`✅ Export complete. Rows processed: ${total}`);
            } catch (e) {
                console.error("Export failed:", e);
                process.exitCode = 1;
            } finally {
                // finish and atomically rename temp files to final names
                await Promise.all(
                    Array.from(writers.values()).map(
                        ({ ws }) =>
                            new Promise((res, rej) =>
                                ws.end(err => (err ? rej(err) : res()))
                            )
                    )
                );

                for (const { tmp, finalPath } of writers.values()) {
                    try {
                        fs.renameSync(tmp, finalPath);
                    } catch (e) {
                    }
                }

            throw new Error("This migration is not revertable");
            }
        }
    };
};
