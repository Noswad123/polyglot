package main

import (
	"fmt"
	"os/ioutil"
	"log"
	"strings"

	"gopkg.in/yaml.v3"
)

// --- Common Structs used across multiple formats ---

// TrackableProgress represents the progress on a trackable item.
// Reused as it's a common structure.
type TrackableProgress struct {
	TrackableID int    `yaml:"trackable_id,omitempty"` // Omitted for XXXByTopLevel where it's implicit
	Status      string `yaml:"status"`
	Notes       string `yaml:"notes,omitempty"`
}

// RelationshipTarget represents a target in a trackable relationship.
type RelationshipTarget struct {
	Name string `yaml:"name"`
	Type string `yaml:"type"`
}

// --- Structs for DBYAMLByTopLevel (formerly Option 1) ---

type LanguageByTopLevel struct {
	ID               int                  `yaml:"id"`
	Name             string               `yaml:"name"`
	Version          string               `yaml:"version,omitempty"`
	DocumentationURL string               `yaml:"documentation_url,omitempty"`
	Description      string               `yaml:"description,omitempty"`
	TrackableInfo    *TrackableProgress   `yaml:"trackable_info,omitempty"`
	Tags             []string             `yaml:"tags,omitempty"`
	Concepts         []ConceptByTopLevel  `yaml:"concepts,omitempty"`
	Relationships    *RelationshipsByTopLevel `yaml:"relationships,omitempty"`
}

type ConceptByTopLevel struct {
	ID            int                  `yaml:"id,omitempty"` // ID might be omitted if nested under language
	Name          string               `yaml:"name"`
	Description   string               `yaml:"description,omitempty"`
	TrackableInfo *TrackableProgress   `yaml:"trackable_info,omitempty"`
	Tags          []string             `yaml:"tags,omitempty"`
	Examples      []ExampleByTopLevel  `yaml:"examples,omitempty"`
	Relationships *RelationshipsByTopLevel `yaml:"relationships,omitempty"`
}

type ExampleByTopLevel struct {
	CodeSnippet string   `yaml:"code_snippet"`
	Explanation string   `yaml:"explanation,omitempty"`
	Language    string   `yaml:"language,omitempty"` // For examples not directly nested under a language
	Tags        []string `yaml:"tags,omitempty"`
}

type TrackableByTopLevel struct { // Used for top-level trackables
	ID            int                  `yaml:"id"`
	Name          string               `yaml:"name"`
	Type          string               `yaml:"type"`
	Description   string               `yaml:"description,omitempty"`
	TrackableInfo *TrackableProgress   `yaml:"trackable_info,omitempty"`
	Tags          []string             `yaml:"tags,omitempty"`
	Relationships *RelationshipsByTopLevel `yaml:"relationships,omitempty"`
}

type RelationshipsByTopLevel struct {
	Uses       []RelationshipTarget `yaml:"uses,omitempty"`
	Includes   []RelationshipTarget `yaml:"includes,omitempty"`
	DependsOn  []RelationshipTarget `yaml:"depends_on,omitempty"`
	Implements []RelationshipTarget `yaml:"implements,omitempty"`
}

// DBYAMLByTopLevel is the root struct for the "grouped by top-level entity" format.
type DBYAMLByTopLevel struct {
	Languages  []LanguageByTopLevel  `yaml:"languages,omitempty"`
	Concepts   []ConceptByTopLevel   `yaml:"concepts,omitempty"`
	Trackables []TrackableByTopLevel `yaml:"trackables,omitempty"`
}

// --- Structs for DBYAMLFlat (formerly Option 2) ---

type LanguageFlat struct {
	ID               int    `yaml:"id"`
	Name             string `yaml:"name"`
	Version          string `yaml:"version,omitempty"`
	DocumentationURL string `yaml:"documentation_url,omitempty"`
	Description      string `yaml:"description,omitempty"`
}

type ConceptFlat struct {
	ID          int    `yaml:"id"`
	Name        string `yaml:"name"`
	Description string `yaml:"description,omitempty"`
}

type ExampleFlat struct {
	ID          int    `yaml:"id"`
	LanguageID  int    `yaml:"language_id,omitempty"` // Use omitempty for nullable foreign keys
	ConceptID   int    `yaml:"concept_id,omitempty"`  // Use omitempty for nullable foreign keys
	CodeSnippet string `yaml:"code_snippet"`
	Explanation string `yaml:"explanation,omitempty"`
}

type TrackableFlat struct {
	ID          int    `yaml:"id"`
	Name        string `yaml:"name"`
	Type        string `yaml:"type"`
	Description string `yaml:"description,omitempty"`
}

type LanguageInfoFlat struct {
	TrackableID      int    `yaml:"trackable_id"`
	Version          string `yaml:"version,omitempty"`
	DocumentationURL string `yaml:"documentation_url,omitempty"`
}

type TagFlat struct {
	ID          int    `yaml:"id"`
	Name        string `yaml:"name"`
	Description string `yaml:"description,omitempty"`
}

type TrackableTagFlat struct {
	TrackableID int `yaml:"trackable_id"`
	TagID       int `yaml:"tag_id"`
}

type TrackableRelationshipFlat struct {
	SourceID int    `yaml:"source_id"`
	TargetID int    `yaml:"target_id"`
	Relation string `yaml:"relation"`
}

type ExampleTagFlat struct {
	ExampleID int `yaml:"example_id"`
	TagID     int `yaml:"tag_id"`
}

// DBYAMLFlat is the root struct for the "flat list by table" format.
type DBYAMLFlat struct {
	Languages              []LanguageFlat              `yaml:"languages,omitempty"`
	Concepts               []ConceptFlat               `yaml:"concepts,omitempty"`
	Examples               []ExampleFlat               `yaml:"examples,omitempty"`
	Trackables             []TrackableFlat             `yaml:"trackables,omitempty"`
	LanguageInfo           []LanguageInfoFlat          `yaml:"language_info,omitempty"`
	Tags                   []TagFlat                   `yaml:"tags,omitempty"`
	TrackableTags          []TrackableTagFlat          `yaml:"trackable_tags,omitempty"`
	TrackableProgress      []TrackableProgress         `yaml:"trackable_progress,omitempty"`
	TrackableRelationships []TrackableRelationshipFlat `yaml:"trackable_relationships,omitempty"`
	ExampleTags            []ExampleTagFlat            `yaml:"example_tags,omitempty"`
}

// --- Structs for DBYAMLByProgress (formerly Option 3) ---

type ProgressSummaryByProgress struct {
	Trackable TrackableSummaryByProgress `yaml:"trackable"`
	Status    string                   `yaml:"status"`
	Notes     string                   `yaml:"notes,omitempty"`
	Details   *TrackableDetailsByProgress `yaml:"details,omitempty"`
}

type TrackableSummaryByProgress struct {
	ID   int    `yaml:"id"`
	Name string `yaml:"name"`
	Type string `yaml:"type"`
}

type TrackableDetailsByProgress struct {
	Version         string   `yaml:"version,omitempty"`
	DocumentationURL string   `yaml:"documentation_url,omitempty"`
	Description     string   `yaml:"description,omitempty"`
	Tags            []string `yaml:"tags,omitempty"`
}

// DBYAMLByProgress is the root struct for the "focus on progress tracking" format.
type DBYAMLByProgress struct {
	ProgressSummary []ProgressSummaryByProgress `yaml:"progress_summary,omitempty"`
}

// --- YAML Format Identifiers (using constants for clarity) ---

const (
	FormatByTopLevel = iota + 1 // Starts at 1
	FormatFlat
	FormatByProgress
)

// --- Common Helper Functions ---

// MarshalDBYAMLData marshals data into a specific YAML format.
func MarshalDBYAMLData(data interface{}, format int) ([]byte, error) {
	var out []byte
	var err error

	switch format {
	case FormatByTopLevel:
		if d, ok := data.(DBYAMLByTopLevel); ok {
			out, err = yaml.Marshal(d)
		} else {
			return nil, fmt.Errorf("data is not of type DBYAMLByTopLevel for format %d", format)
		}
	case FormatFlat:
		if d, ok := data.(DBYAMLFlat); ok {
			out, err = yaml.Marshal(d)
		} else {
			return nil, fmt.Errorf("data is not of type DBYAMLFlat for format %d", format)
		}
	case FormatByProgress:
		if d, ok := data.(DBYAMLByProgress); ok {
			out, err = yaml.Marshal(d)
		} else {
			return nil, fmt.Errorf("data is not of type DBYAMLByProgress for format %d", format)
		}
	default:
		return nil, fmt.Errorf("unsupported YAML format: %d", format)
	}

	if err != nil {
		return nil, fmt.Errorf("failed to marshal YAML for format %d: %w", format, err)
	}
	return out, nil
}

// UnmarshalDBYAMLData attempts to unmarshal YAML data into one of the known formats.
// It returns the unmarshaled data as an interface{} and the detected format number.
func UnmarshalDBYAMLData(yamlData []byte) (interface{}, int, error) {
	// Try DBYAMLByTopLevel
	var dataByTopLevel DBYAMLByTopLevel
	errByTopLevel := yaml.Unmarshal(yamlData, &dataByTopLevel)
	if errByTopLevel == nil {
		// Heuristic: Check for common top-level keys unique to this format
		if strings.Contains(string(yamlData), "languages:") && (len(dataByTopLevel.Languages) > 0 || len(dataByTopLevel.Concepts) > 0 || len(dataByTopLevel.Trackables) > 0) {
			log.Println("Detected YAML format: DBYAMLByTopLevel")
			return dataByTopLevel, FormatByTopLevel, nil
		}
	}

	// Try DBYAMLByProgress (very distinct top-level key)
	var dataByProgress DBYAMLByProgress
	errByProgress := yaml.Unmarshal(yamlData, &dataByProgress)
	if errByProgress == nil {
		if strings.Contains(string(yamlData), "progress_summary:") && len(dataByProgress.ProgressSummary) > 0 {
			log.Println("Detected YAML format: DBYAMLByProgress")
			return dataByProgress, FormatByProgress, nil
		}
	}

	// Try DBYAMLFlat (most generic, has many top-level lists, so try last or with more checks)
	var dataFlat DBYAMLFlat
	errFlat := yaml.Unmarshal(yamlData, &dataFlat)
	if errFlat == nil {
		// Heuristic: Check for a combination of keys expected in Flat format
		// This might need to be more robust based on typical content
		if strings.Contains(string(yamlData), "languages:") &&
			strings.Contains(string(yamlData), "tags:") &&
			strings.Contains(string(yamlData), "trackable_progress:") {
			log.Println("Detected YAML format: DBYAMLFlat")
			return dataFlat, FormatFlat, nil
		}
	}


	// If none of the specific formats match, try to unmarshal into a generic map
	var genericMap map[string]interface{}
	errGeneric := yaml.Unmarshal(yamlData, &genericMap)
	if errGeneric == nil {
		return nil, 0, fmt.Errorf("could not definitively determine YAML format, but it's valid YAML. Top level keys: %v", getMapKeys(genericMap))
	}

	// Return the error from the most likely (or first attempted) unmarshal as a general failure indicator
	return nil, 0, fmt.Errorf("could not unmarshal YAML into any known format. Last errors: ByTopLevel=%v, ByProgress=%v, Flat=%v",
		errByTopLevel, errByProgress, errFlat)
}

func getMapKeys(m map[string]interface{}) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

// Example usage (main function and dummy data for demonstration)
func main() {
	// --- Example Data for Marshalling ---

	// Data for DBYAMLByTopLevel
	dataByTopLevel := DBYAMLByTopLevel{
		Languages: []LanguageByTopLevel{
			{
				ID:               1,
				Name:             "Python",
				Version:          "3.10",
				DocumentationURL: "https://docs.python.org/3/",
				Description:      "A high-level, interpreted programming language.",
				TrackableInfo:    &TrackableProgress{Status: "mastered", Notes: "Used daily."},
				Tags:             []string{"Programming Language", "Scripting"},
				Concepts: []ConceptByTopLevel{
					{Name: "Decorators", Description: "Functions that modify others.",
						Examples: []ExampleByTopLevel{
							{CodeSnippet: "def my_decorator():\n  pass", Explanation: "Simple decorator."},
						},
					},
				},
				Relationships: &RelationshipsByTopLevel{
					Uses: []RelationshipTarget{{Name: "Django", Type: "project"}},
				},
			},
		},
		Concepts: []ConceptByTopLevel{
			{ID: 101, Name: "SQL Joins", Description: "Combining rows.",
				TrackableInfo: &TrackableProgress{Status: "mastered", Notes: "Essential."},
				Tags:          []string{"Databases", "SQL"},
				Examples: []ExampleByTopLevel{
					{CodeSnippet: "SELECT Orders.OrderID, Customers.CustomerName\nFROM Orders\nINNER JOIN Customers ON Orders.CustomerID = Customers.CustomerID;", Explanation: "INNER JOIN example.", Language: "SQL"},
				},
			},
		},
	}

	// Data for DBYAMLFlat (simplified)
	dataFlat := DBYAMLFlat{
		Languages: []LanguageFlat{
			{ID: 1, Name: "Python", Version: "3.10"},
			{ID: 2, Name: "JavaScript", Version: "ES2023"},
		},
		Concepts: []ConceptFlat{
			{ID: 101, Name: "Decorators"},
			{ID: 102, Name: "Closures"},
		},
		TrackableProgress: []TrackableProgress{
			{TrackableID: 1, Status: "mastered", Notes: "Used daily for scripting."},
			{TrackableID: 2, Status: "in progress", Notes: "Focusing on React."},
		},
	}

	// Data for DBYAMLByProgress (simplified)
	dataByProgress := DBYAMLByProgress{
		ProgressSummary: []ProgressSummaryByProgress{
			{
				Trackable: TrackableSummaryByProgress{ID: 1, Name: "Python", Type: "language"},
				Status:    "mastered",
				Notes:     "Used daily for scripting and web development.",
				Details: &TrackableDetailsByProgress{
					Version:         "3.10",
					DocumentationURL: "https://docs.python.org/3/",
					Description:     "A high-level, interpreted programming language.",
					Tags:            []string{"Programming Language", "Scripting", "Backend"},
				},
			},
		},
	}

	fmt.Println("--- Marshalling Examples ---")

	// Marshal DBYAMLByTopLevel
	yamlByTopLevel, err := MarshalDBYAMLData(dataByTopLevel, FormatByTopLevel)
	if err != nil {
		log.Fatalf("Error marshalling DBYAMLByTopLevel: %v", err)
	}
	fmt.Println("\n--- DBYAMLByTopLevel Output ---")
	fmt.Println(string(yamlByTopLevel))

	// Marshal DBYAMLFlat
	yamlFlat, err := MarshalDBYAMLData(dataFlat, FormatFlat)
	if err != nil {
		log.Fatalf("Error marshalling DBYAMLFlat: %v", err)
	}
	fmt.Println("\n--- DBYAMLFlat Output ---")
	fmt.Println(string(yamlFlat))

	// Marshal DBYAMLByProgress
	yamlByProgress, err := MarshalDBYAMLData(dataByProgress, FormatByProgress)
	if err != nil {
		log.Fatalf("Error marshalling DBYAMLByProgress: %v", err)
	}
	fmt.Println("\n--- DBYAMLByProgress Output ---")
	fmt.Println(string(yamlByProgress))

	fmt.Println("\n--- Unmarshalling Examples ---")

	// Unmarshal DBYAMLByTopLevel output
	unmarshaledDataByTopLevel, formatByTopLevel, err := UnmarshalDBYAMLData(yamlByTopLevel)
	if err != nil {
		log.Fatalf("Error unmarshalling DBYAMLByTopLevel: %v", err)
	}
	fmt.Printf("Unmarshaled format %d successfully.\n", formatByTopLevel)
	if d, ok := unmarshaledDataByTopLevel.(DBYAMLByTopLevel); ok {
		fmt.Printf("Number of languages in DBYAMLByTopLevel: %d\n", len(d.Languages))
	}

	// Unmarshal DBYAMLFlat output
	unmarshaledDataFlat, formatFlat, err := UnmarshalDBYAMLData(yamlFlat)
	if err != nil {
		log.Fatalf("Error unmarshalling DBYAMLFlat: %v", err)
	}
	fmt.Printf("Unmarshaled format %d successfully.\n", formatFlat)
	if d, ok := unmarshaledDataFlat.(DBYAMLFlat); ok {
		fmt.Printf("Number of languages in DBYAMLFlat: %d\n", len(d.Languages))
	}

	// Unmarshal DBYAMLByProgress output
	unmarshaledDataByProgress, formatByProgress, err := UnmarshalDBYAMLData(yamlByProgress)
	if err != nil {
		log.Fatalf("Error unmarshalling DBYAMLByProgress: %v", err)
	}
	fmt.Printf("Unmarshaled format %d successfully.\n", formatByProgress)
	if d, ok := unmarshaledDataByProgress.(DBYAMLByProgress); ok {
		fmt.Printf("Number of progress summaries in DBYAMLByProgress: %d\n", len(d.ProgressSummary))
	}

	// Example of importing from a file (you'd replace this with actual file reading)
	dummyYAMLFileContent := `
languages:
  - id: 5
    name: Go
    version: "1.20"
concepts:
  - id: 201
    name: Concurrency
tags:
  - id: 1
    name: Programming
trackable_progress:
  - trackable_id: 5
    status: in progress
`
	err = ioutil.WriteFile("dummy_input.yaml", []byte(dummyYAMLFileContent), 0644)
	if err != nil {
		log.Fatalf("Failed to create dummy file: %v", err)
	}
	defer func() {
		// Clean up the dummy file
		if err := ioutil.Remove("dummy_input.yaml"); err != nil {
			log.Printf("Warning: Could not remove dummy_input.yaml: %v", err)
		}
	}()

	fmt.Println("\n--- Unmarshalling from a dummy file (expected DBYAMLFlat-like) ---")
	fileContent, err := ioutil.ReadFile("dummy_input.yaml")
	if err != nil {
		log.Fatalf("Error reading dummy_input.yaml: %v", err)
	}

	unmarshaledFromFile, formatFromFile, err := UnmarshalDBYAMLData(fileContent)
	if err != nil {
		log.Fatalf("Error unmarshalling from file: %v", err)
	}
	fmt.Printf("Detected format from file: %d\n", formatFromFile)
	if d, ok := unmarshaledFromFile.(DBYAMLFlat); ok {
		fmt.Printf("Languages in file: %+v\n", d.Languages)
	}
}
