//! Python bindings for utter with the vosk wheel's object surface: `Model`, `KaldiRecognizer`
//! (alias `Recognizer`), the same method names, and libvosk-shaped JSON strings, so a host
//! written against vosk selects this package without an adapter.

// The method names are the vosk wheel's, which are CamelCase.
#![allow(non_snake_case)]

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::sync::Arc;

#[pyclass(name = "Model", frozen)]
struct PyModel {
    inner: Arc<utter::Model>,
}

#[pymethods]
impl PyModel {
    #[new]
    fn new(path: &str) -> PyResult<Self> {
        let model = utter::Model::open(std::path::Path::new(path))
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        Ok(PyModel {
            inner: Arc::new(model),
        })
    }

    /// Word id for a word, -1 when the model does not know it (vosk's FindWord).
    fn FindWord(&self, word: &str) -> i64 {
        self.inner.word_ids.get(word).copied().unwrap_or(-1)
    }
}

/// The recognizer owns a clone of the model handle so the borrow lives as long as it does.
#[pyclass(name = "KaldiRecognizer")]
struct PyRecognizer {
    // Declared first so it is dropped before the model handle it borrows from.
    inner: utter::Recognizer<'static>,
    _model: Arc<utter::Model>,
}

fn options(unknown_cost: Option<f32>) -> utter::recognizer::RecognizerOptions {
    utter::recognizer::RecognizerOptions {
        unknown_cost,
        ..Default::default()
    }
}

#[pymethods]
impl PyRecognizer {
    /// `KaldiRecognizer(model, sample_rate, grammar_json)`; the grammar is a JSON array of
    /// strings as vosk takes it. `unknown_cost` adds the model's unknown-word symbol.
    #[new]
    #[pyo3(signature = (model, sample_rate, grammar, unknown_cost = None))]
    fn new(
        model: &PyModel,
        sample_rate: f32,
        grammar: &str,
        unknown_cost: Option<f32>,
    ) -> PyResult<Self> {
        let words = utter::json::parse_string_array(grammar)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        let arc = model.inner.clone();
        // The Arc keeps the model alive for the recognizer's lifetime; the reference handed to
        // the recognizer is derived from it and dropped with it.
        let model_ref: &'static utter::Model = unsafe { &*(Arc::as_ptr(&arc)) };
        let inner =
            utter::Recognizer::with_options(model_ref, sample_rate, &words, &options(unknown_cost))
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(PyRecognizer { inner, _model: arc })
    }

    /// Any value Python considers truthy, as the vosk wheel accepts.
    fn SetWords(&mut self, on: &Bound<'_, PyAny>) -> PyResult<()> {
        self.inner.set_words(on.is_truthy()?);
        Ok(())
    }
    fn SetPartialWords(&mut self, on: &Bound<'_, PyAny>) -> PyResult<()> {
        self.inner.set_partial_words(on.is_truthy()?);
        Ok(())
    }
    fn SetPartialAlternatives(&mut self, n: usize) {
        self.inner.set_alternatives(n);
    }
    fn SetMaxAlternatives(&mut self, n: usize) {
        self.inner.set_max_alternatives(n);
    }

    /// 16-bit little-endian mono PCM. Returns True when an endpoint fired.
    fn AcceptWaveform(&mut self, py: Python<'_>, data: &Bound<'_, PyBytes>) -> PyResult<bool> {
        let bytes = data.as_bytes();
        if bytes.len() % 2 != 0 {
            return Err(PyValueError::new_err(
                "AcceptWaveform wants 16-bit PCM: an even number of bytes",
            ));
        }
        let samples: Vec<i16> = bytes
            .chunks_exact(2)
            .map(|c| i16::from_le_bytes([c[0], c[1]]))
            .collect();
        let step = py.detach(|| self.inner.accept(&samples));
        Ok(step.endpoint)
    }

    /// The sample position of the last decoded frame after the last AcceptWaveform, in samples
    /// fed since construction.
    fn DecodedSample(&self) -> u64 {
        self.inner.decoded_sample()
    }

    fn PartialResult(&mut self) -> String {
        self.inner.partial().to_string()
    }
    fn Result(&mut self) -> String {
        self.inner.result().to_string()
    }
    fn FinalResult(&mut self) -> String {
        self.inner.final_result().to_string()
    }
    fn Reset(&mut self) {
        self.inner.reset();
    }
}

/// vosk's SetLogLevel; utter logs nothing by default, so this only records the request.
#[pyfunction]
fn SetLogLevel(_level: i32) {}

#[pymodule]
fn utterpy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyModel>()?;
    m.add_class::<PyRecognizer>()?;
    m.add("Recognizer", m.getattr("KaldiRecognizer")?)?;
    m.add_function(wrap_pyfunction!(SetLogLevel, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
