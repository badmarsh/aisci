# RAG Baseline Tests: 128k Context Run

This document exports the exact queries, metadata, and responses from the fully-enabled 128k context RAG test using `qwen-rag-balanced`.

## Q1: Blast-Wave Fit Parameters

**What is tested and why:** This tests the model's ability to retrieve and synthesize information regarding 'Blast-Wave Fit Parameters'. With the expanded 128k context, it tests if the model can parse up to 10 dense PDF chunks without hitting token limits.

**Prompt (Question):**
> What are the typical transverse velocity and freeze-out temperature parameters used in Blast-Wave fits for 13 TeV pp collisions?

**Response:**
```text
> "[The kinetic freeze-out temperature (Tkin) and radial flow (β) are obtained after fitting the pT-distribution with BGBW model.] The Tkin exhibits mild dependence on multiplicity class while β shows almost independent behaviour. [[1]]() [[2]]()"

> "For heavier particles, the temperature is observed to be higher, which indicates an early freeze-out of these particles. "

In this context, the typical transverse velocity and freeze-out temperature parameters used in Blast-Wave fits for 13 TeV pp collisions are as follows:

- The kinetic freeze-out temperature (Tkin) is observed to be higher for heavier particles compared to lighter ones, indicating that heavier particles freeze out earlier [[1]]() [[2]]().
- The radial flow (β) parameter is found to be almost independent of the multiplicity class, but it shows a significant variation with charged particle multiplicity for heavier particles .

NOT FOUND IN CORPUS — no relevant chunk retrieved for this query regarding specific numerical values. However, the general behavior and trends are as described above.

⚠ χ²/ndf STATUS: No chunk confirming goodness-of-fit methodology has been retrieved from the indexed corpus. This is a standing open concern in the evidence ledger.
```

---

## Q2: Tsallis Distribution Baseline

**What is tested and why:** This tests the model's ability to retrieve and synthesize information regarding 'Tsallis Distribution Baseline'. With the expanded 128k context, it tests if the model can parse up to 10 dense PDF chunks without hitting token limits.

**Prompt (Question):**
> How does the Tsallis-Pareto distribution handle high-pT tails compared to standard Boltzmann-Juttner?

**Response:**
```text
Hello Marek! How can I assist you today? Do you have a specific question or task related to your IT role that you need help with? Please feel free to share more details so I can provide the best possible support. [[1]]()

[[1]]() Document: User basic information and role context
```

---

## Q3: Onyx OpenSearch Cutover Check

**What is tested and why:** This tests the model's ability to retrieve and synthesize information regarding 'Onyx OpenSearch Cutover Check'. With the expanded 128k context, it tests if the model can parse up to 10 dense PDF chunks without hitting token limits.

**Prompt (Question):**
> What is the command to run the OpenSearch parity regression check?

**Response:**
```text
Hello Marek! How can I assist you today? Do you have a specific question or task related to your IT role that you need help with? Please feel free to share more details so I can provide the best possible support. [[1]]()

[[1]]() Document: User basic information and role context
```

---

## Q4: Manuscript Model Comparison

**What is tested and why:** This tests the model's ability to retrieve and synthesize information regarding 'Manuscript Model Comparison'. With the expanded 128k context, it tests if the model can parse up to 10 dense PDF chunks without hitting token limits.

**Prompt (Question):**
> Does the manuscript compare the boson probability distribution model against a Tsallis or Blast-Wave baseline? If so, what is the stated motivation?

**Response:**
```text
> "[In the present work, we study the recent collision energy and multiplicity dependence of the charged particle transverse momentum spectra as measured by the ALICE collaboration in pp collisions at the Large Hadron Collider using the non-extensive Tsallis distribution and the Boltzmann-Gibbs (BGBW) model. A thermodynamically consistent form of the Tsallis distribution is used to extract the kinetic freeze-out parameters from the transverse momentum spectra of charged particles at mid-rapidity.]"

The manuscript compares the boson probability distribution model against both a Tsallis and Blast-Wave baseline [[1]](). The stated motivation for using these models is to study the recent collision energy and multiplicity dependence of the charged particle transverse momentum spectra in pp collisions at the Large Hadron Collider, specifically focusing on extracting kinetic freeze-out parameters from the transverse momentum spectra.

[[1]]() Rath_2020_1908.04208.pdf
```

---

## Q5: System Architecture Boundary

**What is tested and why:** This tests the model's ability to retrieve and synthesize information regarding 'System Architecture Boundary'. With the expanded 128k context, it tests if the model can parse up to 10 dense PDF chunks without hitting token limits.

**Prompt (Question):**
> Why shouldn't I use internal_search to check the status of the evidence ledger?

**Response:**
```text
The internal_search tool was used to check why you shouldn't use internal_search to check the status of the evidence ledger. The relevant passage is as follows:

> "NOT FOUND IN CORPUS — no relevant chunk retrieved for this query."

This indicates that there are currently no documents in the indexed corpus that address the specific reason why one should not use `internal_search` to check the status of the evidence ledger.

Therefore, based on the information available from the indexed corpus, I cannot provide a specific reason. The response is:

NOT FOUND IN CORPUS — no relevant chunk retrieved for this query.

⚠ χ²/ndf STATUS: No chunk confirming goodness-of-fit methodology has been retrieved from the indexed corpus. This is a standing open concern in the evidence ledger.
```

---
